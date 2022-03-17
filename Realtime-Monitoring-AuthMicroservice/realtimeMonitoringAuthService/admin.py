from django.contrib import admin
from .models import (
    Data,
    Role,
    User,
)

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Data)
