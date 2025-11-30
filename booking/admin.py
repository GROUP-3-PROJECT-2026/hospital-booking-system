from django.contrib import admin

# Register your models here.

from .models import Patient, Test, Booking

admin.site.register(Patient)
admin.site.register(Test)
admin.site.register(Booking)
