from django import forms
from django.core.exceptions import ValidationError
from core.models import Booking, Patient, Test
from core.validators import validate_phone_number, validate_booking_date
from core.services.booking_service import check_duplicate_booking


class BookingForm(forms.ModelForm):
    """Form for creating and updating bookings."""
    
    # Patient fields
    patient_name = forms.CharField(
        max_length=200,
        label='Patient Name',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    age = forms.IntegerField(
        label='Age',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '150'})
    )
    contact = forms.CharField(
        max_length=10,
        label='Contact Number',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0712345678'}),
        validators=[validate_phone_number]
    )
    
    # Booking fields
    test = forms.ModelChoiceField(
        queryset=Test.objects.all(),
        label='Test Type',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select a test type'
    )
    date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        validators=[validate_booking_date]
    )
    time = forms.TimeField(
        label='Time',
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    hospital = forms.CharField(
        max_length=200,
        label='Hospital Name',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Booking
        fields = ['patient_name', 'age', 'contact', 'test', 'date', 'time', 'hospital']

    def clean(self):
        """Custom validation including duplicate booking check."""
        cleaned_data = super().clean()
        patient_name = cleaned_data.get('patient_name')
        age = cleaned_data.get('age')
        contact = cleaned_data.get('contact')
        test = cleaned_data.get('test')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if not all([patient_name, age, contact, test, date, time]):
            return cleaned_data

        # Get or create patient, update if exists
        patient, created = Patient.objects.get_or_create(
            contact=contact,
            defaults={'name': patient_name, 'age': age}
        )
        # Update patient info if it already exists
        if not created:
            patient.name = patient_name
            patient.age = age
            patient.save()

        # Check for duplicate booking
        if self.instance and self.instance.pk:
            # For update, exclude current instance
            existing_booking = Booking.objects.filter(
                patient=patient,
                test=test,
                date=date,
                time=time
            ).exclude(pk=self.instance.pk).exists()
        else:
            # For create, check normally
            existing_booking = check_duplicate_booking(patient, test, date, time)

        if existing_booking:
            raise ValidationError(
                'A booking already exists for this patient, test, date, and time combination. '
                'Please choose a different time or date.'
            )

        # Store patient in cleaned_data for use in save method
        cleaned_data['patient'] = patient
        return cleaned_data

    def save(self, commit=True):
        """Override save to handle patient creation/retrieval."""
        instance = super().save(commit=False)
        patient = self.cleaned_data.get('patient')
        
        if patient:
            instance.patient = patient
        
        if commit:
            instance.save()
        return instance

