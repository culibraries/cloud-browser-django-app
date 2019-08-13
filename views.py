from rest_framework.views import APIView
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_xml.renderers import XMLRenderer
from rest_framework_yaml.renderers import YAMLRenderer
from rest_framework_jsonp.renderers import JSONPRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import permissions
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


class ObjectListView(APIView):
    def get(self, request):
        bucketName = self.request.query_params.get('bname')
        s3 = boto3.resource('s3')
        getBucket = s3.Bucket(bucketName + '/')
        output = []
        for getBucket in getBucket.objects.all():
            output.append({'_id': str(uuid.uuid4), 'name': getBucket['Key']})
        return Response(output)
