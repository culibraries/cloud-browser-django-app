from rest_framework.views import APIView
from rest_framework.response import Response
import json
import boto3
import uuid


class BucketListView(APIView):
    def get(self, request):
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        output = []
        for bucket in response['Buckets']:
            output.append({'_id': str(
                uuid.uuid4()), 'name': bucket['Name'], 'creation_date': bucket['CreationDate']})
        return Response(output)


class ObjectCreateView(APIView):
    def get(self, request):
        s3 = boto3.resource('s3')
        s3.Bucket(request.GET.get('bname')).put_object(
            Key=request.GET.get('key'), Body='', ACL='public-read')
        output = 'Object ' + \
            request.GET.get('bname') + '/' + \
            request.GET.get('key') + ' has been created'
        return Response(output)


class PresignedCreateView(APIView):
    def post(self, request):
        s3 = boto3.client('s3')
        response = s3.generate_presigned_post(request.GET.get('bname'),
                                              request.GET.get('key'))
        return Response(response)


class PresignedCreateURLView(APIView):
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
    def post(self, request):
        s3 = boto3.client('s3')
        s3.upload_file(request.GET.get('fname'), request.GET.get(
            'bname'), request.GET.get('key'))
        output = 'Object has been uploaded succesfully'
        return Response(output)


class ObjectDownloadView(APIView):
    def post(self, request):
        s3 = boto3.client('s3')
        s3.download_file(request.GET.get('bname'), request.GET.get(
            'key'), request.GET.get('fname'))
        output = 'Object has been downloaded succesfully'
        return Response(output)


class ObjectDeleteView(APIView):
    def get(self, request):
        s3 = boto3.client('s3')
        s3.delete_object(Bucket=request.GET.get('bname'),
                         Key=request.GET.get('key'))
        output = 'Object ' + \
            request.GET.get('bname') + '/' + \
            request.GET.get('key') + ' has been delete'
        return Response(output)


class ObjectListView(APIView):
    def get(self, request):
        s3 = boto3.resource('s3')
        getBucket = s3.Bucket(request.GET.get('bname'))
        output = []
        for getBucket in getBucket.objects.all():
            output.append({'name': getBucket.key})
        return Response(output)
