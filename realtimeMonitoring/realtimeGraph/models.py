from django.db import models
from django.db.models.fields import DateTimeField
import datetime
from django.utils import timezone

USER_ROLE_ID = 1


class Role(models.Model):
    name = models.CharField(max_length=16, blank=False, unique=True)
    active = models.BooleanField(default=True)

    def str(self):
        return '{}'.format(self.name)


class User(models.Model):
    login = models.CharField(max_length=50, unique=True, blank=False)
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
    description = models.CharField(max_length=200, blank=True)
    lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    lon = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    active = models.BooleanField(default=True)

    def str(self):
        return '{}'.format(self.name)


class Station(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    city = models.ForeignKey(City, on_delete=models.CASCADE, default=None)
    class Meta:
        unique_together = (('user', 'city'),)
    last_activity = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def str(self):
        return '%s %s %s' % (self.user, self.city, self.last_activity)


class Measurement(models.Model):
    name = models.CharField(max_length=50, blank=False)
    unit = models.CharField(max_length=50, blank=False)
    max_value = models.FloatField(null=True, blank=True, default=None)
    min_value = models.FloatField(null=True, blank=True, default=None)
    active = active = models.BooleanField(default=True)

    def str(self):
        return '{} {}'.format(self.name, self.unit)


class Data(models.Model):
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    value = models.FloatField(blank=False)
    created_at = models.DateTimeField(default=timezone.now)

    def str(self):
        return '{} {}'.format(self.value, self.created_at)

    def toDict(self):
        return {
            'measurement': str(self.measurement),
            'station': str(self.station),
            'value': self.value,
            'created_at': self.created_at
        }
