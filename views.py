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
            output.append({'_id': str(uuid.uuid4()), 'name': bucket['Name']})
        return Response(output)


class BucketCreateView(APIView):
    def get(self, request):
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=request.GET.get('bname'))
        output = 'Bucket ' + request.GET.get('bname') + ' has been created'
        return Response(output)


class ObjectCreateView(APIView):
    def get(self, request):
        s3 = boto3.resource('s3')
        s3.Bucket(request.GET.get('bname')).put_object(
            Key=filename, Body='', ACL='public-read')
        output = 'Object ' + \
            request.GET.get('bname') + '/' + \
            request.GET.get('fname') + ' has been created'
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


class BucketDeleteView(APIView):
    def get(self, request):
        s3 = boto3.client('s3')
        s3.delete_bucket(
            Bucket=request.GET.get('bname')
        )
        output = 'Bucket ' + \
            request.GET.get('bname') + '/' + ' has been delete'
        return Response(output)


class ObjectListView(APIView):
    def get(self, request):
        s3 = boto3.resource('s3')
        getBucket = s3.Bucket(request.GET.get('bname'))
        output = []
        for getBucket in getBucket.objects.all():
            output.append({'name': getBucket.key})
        return Response(output)
