# booking_app/admin.py
from django.contrib import admin
from .models import Patient, TestCatalogue, Booking

# Custom Admin classes for better viewing/filtering
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'age')
    search_fields = ('name', 'contact_number')

class TestCatalogueAdmin(admin.ModelAdmin):
    list_display = ('test_name',)
    search_fields = ('test_name',)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test', 'booking_date', 'booking_time', 'hospital_name')
    list_filter = ('booking_date', 'test')
    search_fields = ('patient__name', 'test__test_name')


# Register models with the custom admin options
admin.site.register(Patient, PatientAdmin)
admin.site.register(TestCatalogue, TestCatalogueAdmin)
admin.site.register(Booking, BookingAdmin)