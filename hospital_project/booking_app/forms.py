# booking_app/forms.py
from django import forms
from datetime import date, timedelta
from .models import Patient, TestCatalogue, Booking

class PatientForm(forms.ModelForm):
    """Form to handle Patient data fields (Name, Age, Contact Number)."""
    class Meta:
        model = Patient
        # Exclude the 'contact_number' from here if you want to handle it 
        # separately, but keeping it in the ModelForm is generally cleaner.
        fields = ['name', 'age', 'contact_number']
        widgets = {
            # Use basic HTML date and time input widgets
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XXXXXXXX'}),
        }

class BookingForm(forms.ModelForm):
    """Form to handle Booking data fields and validation."""
    
    # Override the ModelChoiceField to add a specific class for Bootstrap styling
    test = forms.ModelChoiceField(
        queryset=TestCatalogue.objects.all(),
        label="Test Type",
        empty_label="--- Select Test ---",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Hospital Name can be a predefined choice field for consistency
    HOSPITAL_CHOICES = [
        ('Central', 'Central City Hospital'),
        ('Northwood', 'Northwood Medical Center'),
    ]
    hospital_name = forms.ChoiceField(
        choices=HOSPITAL_CHOICES,
        label="Hospital Name",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Booking
        fields = ['test', 'booking_date', 'booking_time', 'hospital_name']
        widgets = {
            # Use appropriate HTML input types
            'booking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    # Custom Validation for Booking Date (Requirement B)
    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')
        today = date.today()
        max_date = today + timedelta(days=30)
        
        # 1. Booking date must be in the future
        if booking_date < today:
            raise forms.ValidationError("Booking date cannot be in the past.")
        
        # 2. Booking date must fall within the next 30 days
        if booking_date > max_date:
            raise forms.ValidationError("Booking date must be within the next 30 days.")
            
        return booking_date