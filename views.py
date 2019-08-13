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


class ObjectListView(APIView):
    def get(self, request, bname=None):
        if bname:
            s3 = boto3.resource('s3')
            getBucket = s3.Bucket(bname)
            output = []
            for getBucket in getBucket.objects.all():
                output.append({'name': getBucket.key})
            return Response(output)
