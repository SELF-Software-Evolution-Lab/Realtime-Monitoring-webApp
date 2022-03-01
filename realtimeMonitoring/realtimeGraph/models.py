from django.db import models, IntegrityError
from django.db.models.fields import DateTimeField
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
import psycopg2

USER_ROLE_ID = 1


class Role(models.Model):
    name = models.CharField(max_length=16, blank=False, unique=True)
    active = models.BooleanField(default=True)

    def str(self):
        return '{}'.format(self.name)


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
        return '{}'.format(self.login)


class City(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    code = models.CharField(max_length=50, null=True)

    def str(self):
        return '{}'.format(self.name)


class State(models.Model):
    name = models.CharField(max_length=50, unique=False, blank=False)
    code = models.CharField(max_length=50, null=True)

    def str(self):
        return '{}'.format(self.name)


class Country(models.Model):
    name = models.CharField(max_length=50, unique=False, blank=False)
    code = models.CharField(max_length=50, null=True)

    def str(self):
        return '{}'.format(self.name)


class Location(models.Model):
    description = models.CharField(max_length=200, blank=True)
    lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('city', 'state', 'country')

    def str(self):
        return '{}'.format(self.name)


class Measurement(models.Model):
    name = models.CharField(max_length=50, blank=False)
    unit = models.CharField(max_length=50, blank=False)
    max_value = models.FloatField(null=True, blank=True, default=None)
    min_value = models.FloatField(null=True, blank=True, default=None)
    active = active = models.BooleanField(default=True)

    def str(self):
        return '{} {}'.format(self.name, self.unit)


class Station(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, default=None)

    class Meta:
        unique_together = ('user', 'location')
    last_activity = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def str(self):
        return '%s %s %s' % (self.user, self.location, self.last_activity)


class Data(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['base_time', 'station_id', 'measurement_id'], name='unique data measure')
        ]

    def base_time_now():
        now = timezone.now()
        return datetime(now.year, now.month, now.day, now.hour, tzinfo=now.tzinfo)

    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    min_value = models.FloatField(null=True, blank=True, default=None)
    max_value = models.FloatField(null=True, blank=True, default=None)
    length = models.IntegerField(default=0)
    avg_value = models.FloatField(null=True, blank=True, default=None)
    times = ArrayField(models.FloatField(), default=list)
    values = ArrayField(models.FloatField(), default=list)
    base_time = models.DateTimeField(default=base_time_now)
    created_at = models.DateTimeField(auto_now_add=True, primary_key=True)

    def save(self, *args, **kwargs):
        self.save_and_smear_timestamp(*args, **kwargs)

    def save_and_smear_timestamp(self, *args, **kwargs):
        """Recursivly try to save by incrementing the timestamp on duplicate error"""
        try:
            super().save(*args, **kwargs)
        except psycopg2.errors.UniqueViolation as exception:
            # Only handle the error:
            #   psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "1_1_farms_sensorreading_pkey"
            #   DETAIL:  Key ("time")=(2020-10-01 22:33:52.507782+00) already exists.
            if all(k in exception.args[0] for k in ("base_time", "already exists")):
                # Increment the timestamp by 1 µs and try again
                self.base_time = self.base_time + timedelta(microseconds=1)
                self.save_and_smear_timestamp(*args, **kwargs)

    def str(self):
        return '{} {} {} {} {} {} {}'.format(self.values, self.base_time, self.station, self.measurement, self.min_value, self.max_value, self.avg_value)

    def toDict(self):
        return {
            'station': str(self.station),
            'measurement': str(self.measurement),
            'values': self.values,
            'base_time': self.base_time,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'avg_value': self.avg_value
        }
