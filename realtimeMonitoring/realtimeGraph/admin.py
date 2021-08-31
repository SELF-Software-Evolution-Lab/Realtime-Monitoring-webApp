from django.contrib import admin
from . models import City, Data, Measurement, Rol, Station, User

admin.site.register(Rol)
admin.site.register(User)
admin.site.register(City)
admin.site.register(Station)
admin.site.register(Measurement)
admin.site.register(Data)
