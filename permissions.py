from rest_framework import permissions
from api.views import UserGroups
import os


class s3Permission(permissions.BasePermission):
    """
    Create Database and Collections permissions.
    """

    def has_permission(self, request, view):
        try:
            groups=UserGroups(request).groups
            bName = request.GET.get('bname')
            special_case = os.getenv('UCB_ALL_BUCKETS', '').split(',')
            groups=groups + special_case

            if "{0}-rw".format(bName) in groups or "{0}-r".format(bName) in groups:
                return True
            else:
                return False
        except:
            return False

class s3WritePermission(permissions.BasePermission):
    """
    Create Database and Collections permissions.
    """

    def has_permission(self, request, view):
        try:
            groups=UserGroups(request).groups
            bName = request.GET.get('bname')
            groups=groups

            if "{0}-rw".format(bName) in groups:
                return True
            else:
                return False
        except:
            return False