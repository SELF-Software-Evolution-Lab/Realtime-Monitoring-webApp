from django.db import models

# Create your models here.

class User(models.Model):
    login = models.CharField(max_length=50)

    def __str__(self):
        return '{}'.format(self.login)

class Location(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return '{}'.format(self.name)

class Sensor(models.Model):
    variable = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=None)
    
    def __str__(self):
        return '%s %s %s' % (self.variable, self.user, self.location)

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, default=None)
    value = models.FloatField(null=True, blank=True, default=None)
    dateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.value)