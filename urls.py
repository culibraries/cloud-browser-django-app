from django.urls import path
from s3.views import BucketListView, ObjectListView

urlpatterns = [
    path('buckets', BucketListView.as_view()),
    path('objects', ObjectListView.as_view())
]
