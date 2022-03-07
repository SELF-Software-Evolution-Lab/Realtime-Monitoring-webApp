from django.contrib import admin
from .models import (
    City,
    Country,
    Data,
    Location,
    Measurement,
    Role,
    State,
    Station,
    User,
)

admin.site.register(Role)
admin.site.register(User)
admin.site.register(City)
admin.site.register(State)
admin.site.register(Country)
admin.site.register(Location)
admin.site.register(Station)
admin.site.register(Measurement)
admin.site.register(Data)
