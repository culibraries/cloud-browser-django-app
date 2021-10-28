from rest_framework import permissions
from api.views import UserGroups
import os


class s3Permission(permissions.BasePermission):
    """
    Read/Write Perms S3 buckets
    """

    def has_permission(self, request, view):
        groups,user_department=UserGroups().groups(request)
        bName = request.GET.get('bname')
        special_case = os.getenv('UCB_ALL_BUCKETS', '')
        groups=groups + special_case.split(',')
        if "{0}-rw".format(bName) in groups or "{0}-r".format(bName) in groups:
            return True
        else:
            return False

class s3WritePermission(permissions.BasePermission):
    """
    Read/Write Perms S3 buckets
    """

    def has_permission(self, request, view):
        groups,user_department=UserGroups().groups(request)

        bName = request.data.get('bname')
        special_case = os.getenv('UCB_ALL_BUCKETS', '')
        groups=groups + special_case.split(',')
        #print(groups)
        #print(bname)

        if "{0}-rw".format(bName) in groups:
            return True
        else:
            return False