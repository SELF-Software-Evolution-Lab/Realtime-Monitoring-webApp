from django.contrib import admin
from . models import Sensor, Location, User, SensorData

admin.site.register(Sensor)
admin.site.register(Location)
admin.site.register(User)
admin.site.register(SensorData)