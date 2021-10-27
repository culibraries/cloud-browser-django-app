from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.views import UserGroups
from s3.permissions import s3Permission, s3WritePermission
import boto3
import json
import uuid
import os


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
            if permission:
                region = s3.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
                data={ 'name': bucket['Name'], 'permission': permission,
                        'creation_date': bucket['CreationDate']}
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
    permission_classes = (IsAuthenticated,)

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


class ObjectUploadView(APIView):
    permission_classes = (IsAuthenticated,s3WritePermission)

    def post(self, request):
        bName=request.data.get('bname')
        #Get Bucket Location
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        s3 = boto3.client('s3', region_name=region)
        uploadObject = s3.upload_file(request.data.get('fname'), bName, request.data.get('key'))
        return Response(uploadObject)


class ObjectDownloadView(APIView):
    permission_classes = (IsAuthenticated,s3Permission)

    def post(self, request):
        bName=request.data.get('bname')
        #Get Bucket Location
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        s3 = boto3.client('s3', region_name=region)
        downloadObject = s3.download_file(bName, request.data.get(
            'key'), request.data.get('fname'))
        return Response(downloadObject)


class ObjectDeleteView(APIView):
    permission_classes = (IsAuthenticated,s3WritePermission)

    def post(self, request):
        bName=request.data.get('bname')
        #Get Bucket Location
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        s3 = boto3.client('s3', region_name=region)
        deleteObject = s3.delete_object(Bucket=request.data.get('bname'),
                                        Key=request.data.get('key'))
        return Response(deleteObject)


class ObjectListView(APIView):
    permission_classes = (IsAuthenticated,s3Permission)

    def getS3data(self,bName,page_size,prefix,resume_token,region):
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
            if 'NextToken' in result:
                next_token=result['NextToken']
        return {"bucketName":bName,"folders":folders,"items":items,"Prefix":prefix,"token":resume_token,"nextToken":next_token}
     
    def get(self, request):
        # Bucket Name
        bName = request.GET.get('bname')
        prefix = request.GET.get('prefix','')
        default_page_size='50'
        page_size = request.GET.get('page_size',default_page_size)
        if not page_size.isdigit():
            page_size = default_page_size
        token= request.GET.get('token','')
        # set permissions
        groups,user_department=UserGroups().groups(request)
        special_case = os.getenv('UCB_ALL_BUCKETS', '').split(',')
        groups=groups + special_case
        if "{0}-rw".format(bName) in groups:
            permissions="rw"
        else:
            permissions="r"
        s3 = boto3.client('s3')
        region = s3.get_bucket_location(Bucket=bName)['LocationConstraint']
        output=self.getS3data(bName, page_size ,prefix,token,region)
        output['permission']= permissions
        return Response(output)
