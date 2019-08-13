from __future__ import unicode_literals

from django.db import models
from rest_framework import serializers


class Platform(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'platform'


class Publication(models.Model):
    ID = models.IntegerField()
    title = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    platform = models.CharField(max_length=100)
    print_issn = models.CharField(max_length=100)
    online_issn = models.CharField(max_length=100)
    journal_doi = models.CharField(max_length=100)
    proprietary_id = models.CharField(max_length=100)
    period = models.DateField()
    requests = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'counter_result_detail'


class Filter(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    params = models.CharField(max_length=500)
    owner = models.CharField(max_length=20)
    created_at = models.DateField()
    updated_at = models.DateField()

    class Meta:
        managed = False
        db_table = 'filter'


class Title(models.Model):
    id = models.IntegerField()
    title = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'publication'


class Publisher(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'publisher'
