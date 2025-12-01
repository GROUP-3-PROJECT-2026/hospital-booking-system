from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class Patient(models.Model):
    """Model to store patient information."""
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    contact = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^07\d{8}$',
                message='Contact number must start with 07 and be 10 digits long (e.g., 0712345678).'
            )
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.contact})"


class Test(models.Model):
    """Model to store available medical tests."""
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Booking(models.Model):
    """Model to store booking information."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bookings')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    time = models.TimeField()
    hospital = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']
        unique_together = [('patient', 'test', 'date', 'time')]

    def __str__(self):
        return f"{self.patient.name} - {self.test.name} on {self.date} at {self.time}"
