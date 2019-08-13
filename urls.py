from django.urls import path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from s3.views import BucketList

urlpatterns = [
    path('bucket/list', BucketList.as_view()),
]
