from django.urls import path
from s3.views import BucketListView, ObjectListView, BucketCreateView, ObjectCreateView, ObjectDeleteView, BucketDeleteView

urlpatterns = [
    path('buckets', BucketListView.as_view()),
    path('objects', ObjectListView.as_view()),
    path('bucket/create', BucketCreateView.as_view()),
    path('bucket/delete', BucketDeleteView.as_view()),
    path('object/create', ObjectCreateView.as_view()),
    path('object/delete', ObjectDeleteView.as_view())
]
