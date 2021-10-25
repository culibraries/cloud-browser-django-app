from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.views import UserGroups
from permissions import s3Permission, s3WritePermission
import boto3
import json
import uuid
import os


class BucketListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        s3 = boto3.client('s3')
        buckets = s3.list_buckets()
        groups=UserGroups(request).groups
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
                data={'_id': str(uuid.uuid4()), 'name': bucket['Name'], 'permission': permission,
                             'region': region, 'creation_date': bucket['CreationDate']}
                output.append(data)
        return Response(output)


class ObjectCreateView(APIView):
    permission_classes = (IsAuthenticated, s3WritePermission)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3')
        createObject = s3.put_object(Bucket=request.data.get('bname'),
                                     Key=request.data.get('key'))
        return Response(createObject)


class PresignedCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        response = s3.generate_presigned_post(request.data.get('bname'),
                                              request.data.get('key'))
        return Response(response)


class PresignedCreateURLView(APIView):
    permission_classes = (IsAuthenticated,s3Permission)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': request.data.get('bname'),
                'Key': request.data.get('key')
            },
            ExpiresIn=request.data.get('expires')
        )
        return Response(url)


class ObjectUploadView(APIView):
    permission_classes = (IsAuthenticated,s3WritePermission)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        uploadObject = s3.upload_file(request.data.get('fname'), request.data.get(
            'bname'), request.data.get('key'))
        return Response(uploadObject)


class ObjectDownloadView(APIView):
    permission_classes = (IsAuthenticated,s3Permission)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        downloadObject = s3.download_file(request.data.get('bname'), request.data.get(
            'key'), request.data.get('fname'))
        return Response(downloadObject)


class ObjectDeleteView(APIView):
    permission_classes = (IsAuthenticated,s3WritePermission)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        deleteObject = s3.delete_object(Bucket=request.data.get('bname'),
                                        Key=request.data.get('key'))
        return Response(deleteObject)


class ObjectListView(APIView):
    permission_classes = (IsAuthenticated,s3Permission)

    def getS3data(bName,page_size='5' ,prefix='',resume_token='',region=None):
        client = boto3.client('s3', region_name=region)
        paginator = client.get_paginator('list_objects')
        #Get folders
        result=paginator.paginate(Bucket=bName, Delimiter='/',Prefix=prefix,PaginationConfig={'MaxItems': 0})
        folders =[]
        folders=result.build_full_result()
        if 'CommonPrefixes' in folders:
             folders= [d['Prefix'] for d in folders['CommonPrefixes'] if 'Prefix' in d]
        # Get Items
        tok=resume_token 
        result=paginator.paginate(Bucket=bName, Delimiter='/',Prefix=prefix,PaginationConfig={'PageSize': page_size,'MaxItems': page_size,'StartingToken':tok})
        items=result.build_full_result()['Contents']
        #remove Owner
        items=[{k: v for k, v in d.items() if k != 'Owner'} for d in items]
        # Remove CommonPrefixes
        items=[i for i in items if not (i['Key'] in prefix)] 
        next_token=result.resume_token
        return {"bucketName":bName,"folders":folders,"items":items,"Prefix":prefix,"token":resume_token,"nextToken":next_token,"errorCode":0}
        
    def get(self, request):
        # Bucket Name
        bName = request.GET.get('bname')
        prefix = request.GET.get('prefix','')
        resume_token = request.GET.get('token','')
        page_size = request.GET.get('page_size','25')
        region = request.GET.get('region','')
        token= request.GET.get('token','')
        # set permissions
        groups=UserGroups(request).groups
        special_case = os.getenv('UCB_ALL_BUCKETS', '').split(',')
        groups=groups + special_case
        if "{0}-rw".format(bName) in groups:
            permissions="rw"
        else:
            permissions="r"
        output=self.getS3data(bName, page_size=page_size ,prefix=prefix,resume_token=token,region=region)
        return Response(output)
