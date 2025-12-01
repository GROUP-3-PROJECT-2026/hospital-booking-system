from django.contrib import admin
from core.models import Patient, Test, Booking


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'contact', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'contact']
    readonly_fields = ['created_at']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'test', 'date', 'time', 'hospital', 'user', 'created_at']
    list_filter = ['date', 'test', 'hospital', 'created_at']
    search_fields = ['patient__name', 'test__name', 'hospital', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
