from django.urls import path
from s3.views import BucketListView, ObjectListView, BucketCreateView

urlpatterns = [
    path('buckets', BucketListView.as_view()),
    path('objects', ObjectListView.as_view()),
    path('buckets/create', BucketCreateView.as_view())
]
