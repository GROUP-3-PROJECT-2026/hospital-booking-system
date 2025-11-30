from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Q


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('RECEPTIONIST', 'Receptionist'),
        ('ADMIN', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='PATIENT')
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
# ----------------------------
# Patient Model
# ----------------------------
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    contact_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^07\d{8}$', message='Enter a valid 07XXXXXXXX number')]
    )
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name}"

# ----------------------------
# Test Model
# ----------------------------
class Test(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=30, validators=[MinValueValidator(1)])  # in minutes
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# ----------------------------
# Booking Model
# ----------------------------
class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    hospital_name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_bookings'
    )
    class Meta:
        unique_together = ['patient', 'test', 'booking_date', 'booking_time','is_active']
        ordering = ['booking_date', 'booking_time']

    def clean(self):
        # Booking date validation (within next 30 days)
        if self.booking_date < timezone.now().date():
            raise ValidationError("Booking date cannot be in the past.")
        if self.booking_date > timezone.now().date() + timedelta(days=30):
            raise ValidationError("Booking date must be within the next 30 days.")
        # Booking time validation (hospital hours: 08:00 - 17:00)
        if not (timezone.datetime.strptime('08:00', '%H:%M').time() <= self.booking_time <= timezone.datetime.strptime('17:00', '%H:%M').time()):
            raise ValidationError("Booking time must be between 08:00 and 17:00.")

    def __str__(self):
        return f"{self.patient.name} - {self.test.name} - {self.booking_date} {self.booking_time}"


class TimeSlot(models.Model):
    hospital_name = models.CharField(max_length=100)
    slot_date = models.DateField()
    slot_time = models.TimeField()
    duration = models.IntegerField(default=30)  # in minutes
    is_available = models.BooleanField(default=True)
    booking = models.OneToOneField(
        Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='time_slot'
    )
    
    class Meta:
        unique_together = ['hospital_name', 'slot_date', 'slot_time']
        ordering = ['slot_date', 'slot_time']