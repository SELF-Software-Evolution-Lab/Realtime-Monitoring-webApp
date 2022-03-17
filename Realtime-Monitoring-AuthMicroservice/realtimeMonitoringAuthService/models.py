from datetime import datetime
from typing import (
    Any,
    MutableMapping,
    Optional,
)

from django.contrib.postgres.fields import ArrayField
from django.db import models, IntegrityError
from django.utils import timezone

USER_ROLE_ID = 1


class Role(models.Model):
    name = models.CharField(max_length=16, blank=False, unique=True)
    active = models.BooleanField(default=True)

    def str(self):
        return "{}".format(self.name)


class User(models.Model):
    login = models.CharField(
        primary_key=True, max_length=50, unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=60, blank=True)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, default=USER_ROLE_ID)
    active = models.BooleanField(default=True)

    def str(self):
        return "{}".format(self.login)


class DataQuerySet(models.query.QuerySet):

    def get_or_create(
            self, defaults: Optional[MutableMapping[str, Any]] = ..., **kwargs: Any,
    ):
        try:
            return (
                Data.objects.get(**kwargs),
                False,
            )
        except Data.DoesNotExist:
            kwargs.update(defaults or {})
            data = Data(
                **kwargs
            )
            data.save()
            return data, True


class DataManager(models.Manager):
    def get_queryset(self):
        return DataQuerySet(self.model)


class Data(models.Model):
    objects = DataManager()

    def base_time_now(self):
        now = timezone.now()
        return datetime(now.year, now.month, now.day, now.hour, tzinfo=now.tzinfo)

    def timestamp_now(self):
        now = timezone.now()
        return int(now.timestamp() * 1000000)

    time = models.BigIntegerField(default=timestamp_now, primary_key=True)
    base_time = models.DateTimeField(default=base_time_now)
    min_value = models.FloatField(null=True, blank=True, default=None)
    max_value = models.FloatField(null=True, blank=True, default=None)
    length = models.IntegerField(default=0)
    avg_value = models.FloatField(null=True, blank=True, default=None)
    times = ArrayField(models.FloatField(), default=list)
    values = ArrayField(models.FloatField(), default=list)

    def save(self, *args, **kwargs):
        self.save_and_smear_timestamp(*args, **kwargs)

    def save_and_smear_timestamp(self, *args, **kwargs):
        """Recursively try to save by incrementing the timestamp on duplicate error"""
        try:
            super().save(*args, **kwargs)
        except IntegrityError as exception:
            # Only handle the error:
            #   psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "1_1_farms_sensorreading_pkey"
            #   DETAIL:  Key ("time")=(2020-10-01 22:33:52.507782+00) already exists.
            if all(k in exception.args[0] for k in ("time", "already exists")):
                # Increment the timestamp by 1 µs and try again
                self.time = self.time + 1
                self.save_and_smear_timestamp(*args, **kwargs)

    def __str__(self):
        return "Data: %s %s %s %s %s %s %s" % (
            str(self.time),
            str(self.min_value),
            str(self.max_value),
            str(self.length),
            str(self.avg_value),
            str(self.times),
            str(self.values),
        )

    def toDict(self):
        return {
            "times": self.times,
            "values": self.values,
            "base_time": self.base_time,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "avg_value": self.avg_value,
        }
