from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
import boto3
import uuid


class BucketListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        output = []
        groups_set = request.user.groups.filter(name__contains='cubl')
        if groups_set.exists():
            for g in groups_set:
                arrGroupName = g.name.split('-')[:-1]
                groupName = '-'.join(arrGroupName)
                print(groupName)
                for bucket in response['Buckets']:
                    if groupName == bucket['Name']:
                        output.append({'_id': str(
                            uuid.uuid4()), 'name': bucket['Name'], 'permission': g.name.split('-')[-1], 'creation_date': bucket['CreationDate']})
        else:
            output = []
        return Response(output)


class ObjectCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.resource('s3')
        createObject = s3.Bucket(request.GET.get('bname')).put_object(
            Key=request.GET.get('key'), Body='', ACL='public-read')
        return Response(createObject)


class PresignedCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.client('s3')
        response = s3.generate_presigned_post(request.GET.get('bname'),
                                              request.GET.get('key'))
        return Response(response)


class PresignedCreateURLView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.client('s3')
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': request.GET.get('bname'),
                'Key': request.GET.get('key')
            },
            ExpiresIn=request.GET.get('expires')
        )
        return Response(url)


class ObjectUploadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.client('s3')
        uploadObject = s3.upload_file(request.GET.get('fname'), request.GET.get(
            'bname'), request.GET.get('key'))
        return Response(uploadObject)


class ObjectDownloadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.client('s3')
        downloadObject = s3.download_file(request.GET.get('bname'), request.GET.get(
            'key'), request.GET.get('fname'))
        return Response(downloadObject)


class ObjectDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.client('s3')
        deleteObject = s3.delete_object(Bucket=request.GET.get('bname'),
                                        Key=request.GET.get('key'))
        return Response(deleteObject)


class ObjectListView(APIView):
    def get(self, request):
        s3 = boto3.resource('s3')
        getBucket = s3.Bucket(request.GET.get('bname'))
        output = []
        for getBucket in getBucket.objects.all():
            output.append(
                {'name': request.GET.get('bname') + '/' + getBucket.key, 'last_modified': getBucket.last_modified, 'size': getBucket.size})
        return Response(output)


class ObjectFolderListView(APIView):
    def get(self, request):
        s3 = boto3.client('s3')
        bName = request.GET.get('bname')
        key = request.GET.get('key')
        folders = []
        items = []
        if (key == '' or key is None):
            resp = s3.list_objects_v2(Bucket=bName, Prefix='', Delimiter="/")
        else:
            resp = s3.list_objects_v2(
                Bucket=bName, Prefix=key, Delimiter="/")
            # if (resp.get('CommonPrefixes') is not None):
            #     folderFinal = []
            #     for item in resp['CommonPrefixes']:
            #         folderFinal = item['Prefix'].split('/')
            #         folders.append(
            #             {'name': folderFinal[1] + '/', 'last_modified': '', 'size': '-'})
            # if (resp.get('Contents') is not None):
            #     itemFinal = []
            #     for item in resp['Contents']:
            #         itemFinal = item['Key'].split('/')
            #         items.append(
            #             {'name': itemFinal[1] + '/', 'last_modified': item['LastModified'], 'size': item['Size']})
        if (resp.get('CommonPrefixes') is not None):
            for item in resp['CommonPrefixes']:
                folders.append(
                    {'name': item['Prefix'], 'last_modified': '', 'size': '-'})
        if (resp.get('Contents') is not None):
            for item in resp['Contents']:
                items.append(
                    {'name': item['Key'], 'last_modified': item['LastModified'], 'size': item['Size']})
        return Response(folders+items)
