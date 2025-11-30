from django.db import models

# Create your models here.
from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Test(models.Model):
    TEST_CHOICES = [
        ('X-Ray', 'X-Ray'),
        ('Ultrasound', 'Ultrasound'),
        ('Blood Test', 'Blood Test'),
    ]

    name = models.CharField(max_length=50, choices=TEST_CHOICES)

    def __str__(self):
        return self.name


class Booking(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    hospital_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('patient', 'test', 'date', 'time')  # Prevent double booking

    def __str__(self):
        return f"{self.patient.name} - {self.test.name} on {self.date} at {self.time}"

