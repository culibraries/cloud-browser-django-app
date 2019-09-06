from django.urls import path
from s3.views import BucketListView, ObjectListView, BucketCreateView, ObjectCreateView, ObjectDeleteView, BucketDeleteView, ObjectUploadView, ObjectDownloadView, PresignedCreateView, PresignedCreateURLView

urlpatterns = [
    path('buckets', BucketListView.as_view(), name='buckets-list'),
    path('bucket', BucketListView.as_view(), name='buckets-list'),

    path('objects', ObjectListView.as_view(), name='objects-list'),
    # path('bucket/create', BucketCreateView.as_view()),
    # path('bucket/delete', BucketDeleteView.as_view()),
    path('object/create', ObjectCreateView.as_view()),
    path('object/delete', ObjectDeleteView.as_view()),
    path('object/upload', ObjectUploadView.as_view(), name='object-upload'),
    path('object/download', ObjectDownloadView.as_view(), name='object-download'),
    path('presigned/create', PresignedCreateView.as_view()),
    path('presigned-url/create', PresignedCreateURLView.as_view())

]
