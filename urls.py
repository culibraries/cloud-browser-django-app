from django.urls import path
from s3.views import BucketListView, ObjectListView, ObjectCreateView, ObjectDeleteView, PresignedCreateView, PresignedCreateURLView

urlpatterns = [
    path('buckets', BucketListView.as_view(), name='buckets-list'),
    path('objects', ObjectListView.as_view(), name='objects-list'),
    path('object/create', ObjectCreateView.as_view()),
    path('object/delete', ObjectDeleteView.as_view()),
    path('presigned/create', PresignedCreateView.as_view()),
    path('presigned-url/create', PresignedCreateURLView.as_view()),
    path('objects', ObjectListView.as_view(),name='objects-list')
]
