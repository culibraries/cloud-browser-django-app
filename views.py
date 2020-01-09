from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import boto3
import json
import uuid


class BucketListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        output = []
        user_groups = []
        for g in request.user.groups.all():
            user_groups.append(g.name)
        if 'samlUserdata' in request.session:
            samlUserdata = request.session['samlUserdata']
            if "urn:oid:1.3.6.1.4.1.632.11.2.200" in samlUserdata:
                grouper = samlUserdata['urn:oid:1.3.6.1.4.1.632.11.2.200']
                user_groups = list(set(user_groups+grouper))
        groups_set = [s for s in user_groups if "cubl" in s]

        if len(groups_set) > 0:
            for g in groups_set:
                arrGroupName = g.split('-')[:-1]
                groupName = '-'.join(arrGroupName)
                for bucket in response['Buckets']:
                    if groupName == bucket['Name']:
                        region = s3.get_bucket_location(Bucket=bucket['Name'])[
                            'LocationConstraint']
                        if region is None:
                            region = 'us-east-1'
                        output.append({'_id': str(
                            uuid.uuid4()), 'name': bucket['Name'], 'permission': g.split('-')[-1], 'region': region, 'creation_date': bucket['CreationDate']})
        else:
            output = []
        return Response(output)


class ObjectCreateView(APIView):
    permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        uploadObject = s3.upload_file(request.data.get('fname'), request.data.get(
            'bname'), request.data.get('key'))
        return Response(uploadObject)


class ObjectDownloadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        downloadObject = s3.download_file(request.data.get('bname'), request.data.get(
            'key'), request.data.get('fname'))
        return Response(downloadObject)


class ObjectDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        deleteObject = s3.delete_object(Bucket=request.data.get('bname'),
                                        Key=request.data.get('key'))
        return Response(deleteObject)


class ObjectListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        region = request.data.get('region')
        s3 = boto3.client('s3', region_name=region)
        bName = request.GET.get('bname')
        key = request.GET.get('key')
        token = request.GET.get('token')
        maxKeys = 2000
        folders = []
        items = []
        output = {
            'token': '',
            'nextToken': '',
            'data': []
        }
        user_groups = []
        for g in request.user.groups.all():
            user_groups.append(g.name)
        if 'samlUserdata' in request.session:
            samlUserdata = request.session['samlUserdata']
            if "urn:oid:1.3.6.1.4.1.632.11.2.200" in samlUserdata:
                grouper = samlUserdata['urn:oid:1.3.6.1.4.1.632.11.2.200']
                user_groups = list(set(user_groups+grouper))
        groups_set = [s for s in user_groups if bName in s]
        if len(groups_set) > 0:
            for g in groups_set:
                permission = g.name('-')[-1]
        else:
            permission = ''
        if (key == '' or key is None):
            if token is not None:
                resp = s3.list_objects_v2(
                    Bucket=bName, Prefix='', Delimiter="/", MaxKeys=maxKeys, ContinuationToken=token.replace(" ", "+"))
            else:
                resp = s3.list_objects_v2(
                    Bucket=bName, Prefix='', Delimiter="/", MaxKeys=maxKeys)
            if 'ContinuationToken' in resp:
                output['token'] = resp['ContinuationToken']
            else:
                output['token'] = ''
            if 'NextContinuationToken' in resp:
                output['nextToken'] = resp['NextContinuationToken']
            else:
                output['nextToken'] = ''
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
                Bucket=bName, Prefix=key, Delimiter="/", MaxKeys=maxKeys)
            if 'ContinuationToken' in resp:
                output['token'] = resp['ContinuationToken']
            else:
                output['token'] = ''
            if 'NextContinuationToken' in resp:
                output['nextToken'] = resp['NextContinuationToken']
            else:
                output['nextToken'] = ''
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
        output['data'] = folders + items
        return Response(output)
