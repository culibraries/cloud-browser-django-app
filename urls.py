from django.urls import path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from s3.views import BucketList

router = routers.SimpleRouter()
router.register('list', BucketList, basename='bucket-list')

urlpatterns = router.urls
