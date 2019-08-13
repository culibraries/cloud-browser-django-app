from django.urls import path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from s3.views import BucketListView, ObjectListView

urlpatterns = [
    path('buckets', BucketListView.as_view()),
    path('^objects/(?P<bname>.+)/$', ObjectListView.as_view())
]
