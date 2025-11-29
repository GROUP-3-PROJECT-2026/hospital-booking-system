# booking_app/models.py
from django.db import models
from django.core.validators import RegexValidator

# Validator to enforce the 07XXXXXXXX format for contact number
contact_validator = RegexValidator(
    regex=r'^07\d{8}$', 
    message="Contact number must be 10 digits starting with '07'."
)

class Patient(models.Model):
    """Stores basic demographic information for a patient."""
    name = models.CharField(max_length=100, verbose_name="Patient Name")
    age = models.IntegerField(verbose_name="Age")
    contact_number = models.CharField(
        max_length=10, 
        validators=[contact_validator],
        unique=True, # Ensure unique contact number for easier patient identification
        verbose_name="Contact Number"
    )

    def __str__(self):
        return self.name

class TestCatalogue(models.Model):
    """Stores the list of available medical tests."""
    test_name = models.CharField(max_length=100, unique=True, verbose_name="Test Type")
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return self.test_name

class Booking(models.Model):
    """Stores the actual booking details."""
    # Relationships
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test = models.ForeignKey(TestCatalogue, on_delete=models.PROTECT) # Protects against deleting a Test that has existing bookings

    # Booking details
    booking_date = models.DateField(verbose_name="Date")
    booking_time = models.TimeField(verbose_name="Time Slot")
    hospital_name = models.CharField(max_length=100, verbose_name="Hospital Name")
    
    # CRITICAL: Enforce unique combination to prevent duplicate bookings
    class Meta:
        unique_together = ('patient', 'test', 'booking_date', 'booking_time')
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"{self.patient.name} - {self.test.test_name} on {self.booking_date}"
