from django.contrib import admin
from .models import UserProfile, Patient, Test, Booking

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone_number']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'contact_number', 'email', 'created_at']
    search_fields = ['name', 'contact_number', 'email']
    list_filter = ['created_at']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'test', 'booking_date', 'booking_time', 'hospital_name', 'status']
    list_filter = ['status', 'booking_date', 'hospital_name']
    search_fields = ['patient__name', 'test__name', 'hospital_name']
    date_hierarchy = 'booking_date'