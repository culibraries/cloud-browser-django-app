from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.views import UserGroups
from s3.permissions import s3Permission, s3WritePermission
import boto3
import json
import uuid
import os
import textwrap, hashlib


class BucketListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        s3 = boto3.client('s3')
        buckets = s3.list_buckets()
        groups,user_department=UserGroups().groups(request)
        special_case = os.getenv('UCB_ALL_BUCKETS', '').split(',')
        groups=groups + special_case
        output = []
        groupset = [s for s in groups if "cubl-" in s]
        for bucket in buckets['Buckets']:
            if "{0}-rw".format(bucket['Name']) in groupset:
                permission='rw'
            elif  "{0}-r".format(bucket['Name']) in groupset:
                permission='r'
            else:
                permission=''
            if "{0}-r".format(bucket['Name']) in special_case:
                exclude=True
                if not permission == 'rw':
                    permission='r'
            else:
                exclude=False
            if permission:
                data={ 'name': bucket['Name'], 'permission': permission,
                        'creation_date': bucket['CreationDate'],'exclude':exclude}
                output.append(data)
        return Response(output)


class ObjectCreateView(APIView):
    permission_classes = (IsAuthenticated, s3WritePermission)

    def post(self, request):
        bName=request.data.get('bname')
        #Get Bucket Location
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        s3 = boto3.client('s3', region_name=region)
        createObject = s3.put_object(Bucket=bName,Key=request.data.get('key'))
        return Response(createObject)


class PresignedCreateView(APIView):
    permission_classes = (IsAuthenticated,s3WritePermission)

    def post(self, request):
        bName=request.data.get('bname')
        #Get Bucket Location
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        s3 = boto3.client('s3', region_name=region)
        response = s3.generate_presigned_post(bName,request.data.get('key'))
        return Response(response)


class PresignedCreateURLView(APIView):
    permission_classes = (IsAuthenticated,s3Permission)

    def post(self, request):
        bName=request.data.get('bname')
        #Get Bucket Location
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        s3 = boto3.client('s3', region_name=region)
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bName,
                'Key': request.data.get('key')
            },
            ExpiresIn=request.data.get('expires')
        )
        return Response(url)

class ObjectDeleteView(APIView):
    permission_classes = (IsAuthenticated,s3WritePermission)

    def post(self, request):
        bName=request.data.get('bname')
        #Get Bucket Location
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        s3client = boto3.client('s3', region_name=region)
        s3resource = boto3.resource('s3', region_name=region)
        delete_keys = {'Objects' : []}
        for p in request.data.get('prefix'):
            objects_to_delete = s3resource.meta.client.list_objects(Bucket=bName, Prefix=p)
            delete_keys['Objects'] = [{'Key' : k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]
            s3resource.meta.client.delete_objects(Bucket=bName, Delete=delete_keys)
        for key in request.data.get("keys"):
            deleteObject = s3client.delete_object(Bucket=bName,Key=key)
        delete_keys=list(set(request.data.get('prefix') + request.data.get("keys") ))
        return Response(delete_keys)


class ObjectListView(APIView):
    permission_classes = (IsAuthenticated,s3Permission)

    def genHash(self,key,split=7):
        r=hashlib.md5(key.encode())
        hashpath="/".join(textwrap.wrap(r.hexdigest(),split))
        return hashpath

    def getS3data(self,request,bName,page_size,prefix,resume_token,region):
        client = boto3.client('s3', region_name=region)
        paginator = client.get_paginator('list_objects')
        #Get folders
        result=paginator.paginate(Bucket=bName, Delimiter='/',Prefix=prefix,PaginationConfig={'MaxItems': 0})
        folders =[]
        result=result.build_full_result()
        if 'CommonPrefixes' in result:
            folders= [d['Prefix'] for d in result['CommonPrefixes'] if 'Prefix' in d]
        # Get Items
        tok=resume_token 
        result=paginator.paginate(Bucket=bName, Delimiter='/',Prefix=prefix,PaginationConfig={'PageSize': page_size,'MaxItems': page_size,'StartingToken':tok})
        result=result.build_full_result()
        items=[]
        next_token=''
        if 'Contents' in result:
            items=result['Contents']
            #remove Owner
            items=[{k: v for k, v in d.items() if k != 'Owner'} for d in items]
            # Remove CommonPrefixes
            items=[i for i in items if not (i['Key'] in prefix)] 
            # Add Thumbnail
            thumbnail_buckets = os.getenv('UCB_THUMBNAIL_BUCKETS', '').split(',')
            if bName in thumbnail_buckets:
                base_url = request.build_absolute_uri('/')[:-1]
                temp=[]
                for d in items:
                    hashpath=self.genHash("{0}/{1}".format(bName,d['Key']))
                    d['thumbnail']="{0}/static/thumbnails/{1}/thumbnail.png".format(base_url,hashpath)
                    temp.append(d)
                items=temp
            if 'NextToken' in result:
                next_token=result['NextToken']
        return {"bucketName":bName,"folders":folders,"items":items,"Prefix":prefix,"token":resume_token,"nextToken":next_token}
     
    def post(self, request):
        # Bucket Name
        bName = request.data.get('bname')
        prefix = request.data.get('prefix','')
        default_page_size='150'
        page_size = request.data.get('page_size',default_page_size)
        if not page_size.isdigit():
            page_size = default_page_size
        token= request.data.get('token','')
        # set permissions
        groups,user_department=UserGroups().groups(request)
        special_case = os.getenv('UCB_ALL_BUCKETS', '').split(',')
        license_case = os.getenv('UCB_LICENSE_BUCKETS', '').split(',')
        groups=groups + special_case
        if "{0}-rw".format(bName) in groups:
            permissions="rw"
            
        else:
            permissions="r"
        licensed=False
        if bName in license_case:
            licensed=True
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        output=self.getS3data(request,bName, page_size ,prefix,token,region)
        output['permission']= permissions
        output['licensed']=licensed
        return Response(output)
