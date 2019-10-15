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
        s3 = boto3.client('s3')
        deleteObject = s3.put_object(Bucket=request.data.get('bname'),
                                     Key=request.data.get('key'), Body='', ACL='public-read')
        return Response(createObject)


class PresignedCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.client('s3')
        response = s3.generate_presigned_post(request.data.get('bname'),
                                              request.data.get('key'))
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
        uploadObject = s3.upload_file(request.data.get('fname'), request.data.get(
            'bname'), request.data.get('key'))
        return Response(uploadObject)


class ObjectDownloadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.client('s3')
        downloadObject = s3.download_file(request.data.get('bname'), request.data.get(
            'key'), request.data.get('fname'))
        return Response(downloadObject)


class ObjectDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        s3 = boto3.client('s3')
        deleteObject = s3.delete_object(Bucket=request.data.get('bname'),
                                        Key=request.data.get('key'))
        return Response(deleteObject)


class ObjectListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        s3 = boto3.resource('s3')
        getBucket = s3.Bucket(request.GET.get('bname'))
        output = []
        for getBucket in getBucket.objects.all():
            output.append(
                {'name': request.GET.get('bname') + '/' + getBucket.key, 'last_modified': getBucket.last_modified, 'size': getBucket.size})
        return Response(output)


class ObjectFolderListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        s3 = boto3.client('s3')
        bName = request.GET.get('bname')
        key = request.GET.get('key')
        folders = []
        items = []
        groups_set = request.user.groups.filter(name__contains=bName)
        if groups_set.exists():
            for g in groups_set:
                permission = g.name.split('-')[-1]
        else:
            permission = ''
        print(groups_set)
        if (key == '' or key is None):
            resp = s3.list_objects_v2(Bucket=bName, Prefix='', Delimiter="/")

            if (resp.get('CommonPrefixes') is not None):
                for item in resp['CommonPrefixes']:
                    folders.append(
                        {'name': item['Prefix'], 'permission': permission,  'last_modified': '', 'size': 0, 'full_path': bName + '/' + item['Prefix'], 'path': item['Prefix']})
            if (resp.get('Contents') is not None):
                for item in resp['Contents']:
                    items.append(
                        {'name': item['Key'], 'permission': permission, 'last_modified': item['LastModified'], 'size': item['Size'], 'full_path': bName + '/' + item['Key'], 'path': item['Key']})
        else:
            numberOfSlash = len(key.split('/')) - 1
            resp = s3.list_objects_v2(
                Bucket=bName, Prefix=key, Delimiter="/")
            if (resp.get('CommonPrefixes') is not None):
                for item in resp['CommonPrefixes']:
                    name = item['Prefix'].split('/')
                    for i in range(numberOfSlash):
                        del name[0]
                    out = '/'.join(name)
                    folders.append(
                        {'name': out, 'permission': permission, 'last_modified': '', 'size': 0, 'full_path': bName + '/' + item['Prefix'], 'path': item['Prefix']})
            if (resp.get('Contents') is not None):
                for item in resp['Contents']:
                    name = item['Key'].split('/')
                    for i in range(numberOfSlash):
                        del name[0]
                    out = '/'.join(name)
                    if out == '':
                        if resp.get('CommonPrefixes') is None:
                            folders = []
                            items = []
                    else:
                        items.append(
                            {'name': out, 'permission': permission, 'last_modified': item['LastModified'], 'size': item['Size'], 'full_path': bName + '/' + item['Key'], 'path': item['Key']})

        return Response(folders+items)
