from django import forms
from core.models import Booking, Patient, Test, UserProfile, TimeSlot
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta, datetime
import re

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}))
    
    # Patient-specific fields (only required when registering as patient)
    patient_name = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    patient_age = forms.IntegerField(
        required=False, 
        min_value=0, 
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'})
    )
    patient_contact = forms.CharField(
        max_length=10, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XXXXXXXX'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        password = cleaned_data.get('password')
        
        # Password strength validation
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # If registering as patient, require patient details
        if role == 'PATIENT':
            patient_name = cleaned_data.get('patient_name')
            patient_age = cleaned_data.get('patient_age')
            patient_contact = cleaned_data.get('patient_contact')
            
            if not patient_name:
                raise forms.ValidationError("Patient name is required for patient registration.")
            if not patient_age:
                raise forms.ValidationError("Patient age is required for patient registration.")
            if not patient_contact:
                raise forms.ValidationError("Patient contact number is required for patient registration.")
            
            # Validate contact number format
            if patient_contact and not re.match(r'^07\d{8}$', patient_contact):
                raise forms.ValidationError("Enter a valid 07XXXXXXXX number for patient contact.")
            
            # Check if patient with same contact already exists
            if Patient.objects.filter(contact_number=patient_contact, is_active=True).exists():
                raise forms.ValidationError("A patient with this contact number already exists.")
        
        return cleaned_data

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Create user profile
            user_profile = UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone_number=self.cleaned_data['phone_number']
            )
            
            # If registering as patient, create patient record linked to user
            if self.cleaned_data['role'] == 'PATIENT':
                Patient.objects.create(
                    user=user,
                    name=self.cleaned_data['patient_name'],
                    age=self.cleaned_data['patient_age'],
                    contact_number=self.cleaned_data['patient_contact'],
                    email=user.email
                )
        return user

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'contact_number', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XXXXXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (optional)'}),
        }
    
    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if contact_number and not re.match(r'^07\d{8}$', contact_number):
            raise forms.ValidationError("Enter a valid 07XXXXXXXX number.")
        
        # Check for duplicate active patients with same contact number
        if contact_number:
            existing = Patient.objects.filter(contact_number=contact_number, is_active=True)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("A patient with this contact number already exists.")
        
        return contact_number

class BookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name != 'is_active':  # Don't add to hidden fields
                field.widget.attrs['class'] = 'form-control'
        
        # Set minimum date for booking date field
        self.fields['booking_date'].widget.attrs['min'] = timezone.now().date().isoformat()
        self.fields['booking_date'].widget.attrs['max'] = (timezone.now().date() + timedelta(days=30)).isoformat()

    class Meta:
        model = Booking
        fields = ['patient', 'test', 'booking_date', 'booking_time', 'hospital_name', 'status']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'hospital_name': forms.TextInput(attrs={'placeholder': 'Hospital Name'}),
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data['booking_date']
        today = timezone.now().date()
        
        if booking_date < today:
            raise forms.ValidationError("Booking date cannot be in the past.")
        if booking_date > today + timedelta(days=30):
            raise forms.ValidationError("Booking date must be within the next 30 days.")
        
        # Check if booking date is on a weekend (optional business rule)
        if booking_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            raise forms.ValidationError("Bookings are not available on weekends.")
        
        return booking_date

    def clean_booking_time(self):
        booking_time = self.cleaned_data['booking_time']
        
        # Hospital hours validation (8:00 AM - 5:00 PM)
        start_time = datetime.strptime('08:00', '%H:%M').time()
        end_time = datetime.strptime('17:00', '%H:%M').time()
        
        if not (start_time <= booking_time <= end_time):
            raise forms.ValidationError("Booking time must be between 08:00 and 17:00.")
        
        return booking_time

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        test = cleaned_data.get('test')
        booking_date = cleaned_data.get('booking_date')
        booking_time = cleaned_data.get('booking_time')
        hospital_name = cleaned_data.get('hospital_name')
        booking_id = self.instance.id if self.instance else None

        # Check for duplicate active bookings
        if all([patient, test, booking_date, booking_time]):
            existing = Booking.objects.filter(
                patient=patient, 
                test=test, 
                booking_date=booking_date, 
                booking_time=booking_time,
                is_active=True  # Only check active bookings
            )
            if booking_id:
                existing = existing.exclude(id=booking_id)
            
            if existing.exists():
                raise forms.ValidationError(
                    "This patient already has an active booking for this test at the selected date and time."
                )

        # Check time slot availability
        if all([hospital_name, booking_date, booking_time, test]):
            if not self.is_time_slot_available(hospital_name, booking_date, booking_time, test, booking_id):
                raise forms.ValidationError(
                    "This time slot is not available. Please choose a different time or hospital."
                )

        return cleaned_data

    def is_time_slot_available(self, hospital_name, date, time, test, booking_id=None):
        """
        Check if the time slot is available considering test duration and existing bookings
        """
        # Calculate end time based on test duration
        start_datetime = datetime.combine(date, time)
        end_datetime = start_datetime + timedelta(minutes=test.duration)
        
        # Check for overlapping bookings at the same hospital
        overlapping_bookings = Booking.objects.filter(
            hospital_name=hospital_name,
            booking_date=date,
            is_active=True
        ).exclude(id=booking_id)  # Exclude current booking when updating
        
        for booking in overlapping_bookings:
            booking_start = datetime.combine(booking.booking_date, booking.booking_time)
            booking_end = booking_start + timedelta(minutes=booking.test.duration)
            
            # Check for time overlap
            if (start_datetime < booking_end) and (end_datetime > booking_start):
                return False
        
        return True

    def save(self, commit=True):
        """
        Override save to handle soft delete and time slot management
        """
        booking = super().save(commit=False)
        
        # Set created_by if it's a new booking
        if not booking.pk and hasattr(self, 'request_user'):
            # This would be set in the view before form validation
            pass
        
        if commit:
            booking.save()
            
            # Create or update time slot
            self.update_time_slot(booking)
        
        return booking

    def update_time_slot(self, booking):
        """
        Create or update time slot for this booking
        """
        if booking.is_active:
            # Create or update time slot
            time_slot, created = TimeSlot.objects.get_or_create(
                hospital_name=booking.hospital_name,
                slot_date=booking.booking_date,
                slot_time=booking.booking_time,
                defaults={
                    'duration': booking.test.duration,
                    'is_available': False,
                    'booking': booking
                }
            )
            if not created:
                time_slot.booking = booking
                time_slot.is_available = False
                time_slot.duration = booking.test.duration
                time_slot.save()
        else:
            # If booking is soft deleted, free up the time slot
            TimeSlot.objects.filter(booking=booking).update(
                is_available=True,
                booking=None
            )

class BookingRestoreForm(forms.Form):
    """
    Simple form for restoring soft-deleted bookings
    """
    confirm = forms.BooleanField(
        required=True,
        label="Confirm restoration",
        help_text="Check this box to confirm you want to restore this booking."
    )

class TimeSlotForm(forms.ModelForm):
    """
    Form for managing time slots (admin use)
    """
    class Meta:
        model = TimeSlot
        fields = ['hospital_name', 'slot_date', 'slot_time', 'duration', 'is_available']
        widgets = {
            'slot_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'slot_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Name'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        hospital_name = cleaned_data.get('hospital_name')
        slot_date = cleaned_data.get('slot_date')
        slot_time = cleaned_data.get('slot_time')
        slot_id = self.instance.id if self.instance else None
        
        # Check for duplicate time slots
        if all([hospital_name, slot_date, slot_time]):
            existing = TimeSlot.objects.filter(
                hospital_name=hospital_name,
                slot_date=slot_date,
                slot_time=slot_time
            )
            if slot_id:
                existing = existing.exclude(id=slot_id)
            
            if existing.exists():
                raise forms.ValidationError(
                    "A time slot already exists for this hospital, date, and time combination."
                )
        
        return cleaned_data