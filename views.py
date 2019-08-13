from rest_framework import viewsets, filters
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


class BucketList(APIView):
    def get(self, request):
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        output = {}
        for bucket in response['Buckets']:
            output['creationDate'] = bucket['CreationDate']
            output['bucketName'] = bucket['Name']
        return json.dumps(output)
