from django.urls import path
from s3.views import BucketListView, ObjectListView, BucketCreateView, EmptyObjectCreateView

urlpatterns = [
    path('buckets', BucketListView.as_view()),
    path('objects', ObjectListView.as_view()),
    path('bucket/create', BucketCreateView.as_view()),
    path('emptyobject/create', EmptyObjectCreateView.as_view())
]
