from django import forms
from .models import Patient, Test, Booking

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'contact_number']

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['patient', 'test', 'date', 'time', 'hospital_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
