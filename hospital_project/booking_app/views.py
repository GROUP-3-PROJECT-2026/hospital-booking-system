# booking_app/views.py
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import PatientForm, BookingForm
from .models import Patient, Booking

@require_http_methods(["GET", "POST"])
def book_test_view(request):
    patient_form = PatientForm(request.POST or None)
    booking_form = BookingForm(request.POST or None)

    if request.method == 'POST':
        # Check if both forms are valid based on their respective Model/Field validators
        if patient_form.is_valid() and booking_form.is_valid():
            
            # --- Day 3 Logic Placeholder: Check for Duplicate Booking will go here ---
            # For now, we proceed straight to saving.

            # 1. Handle Patient (find existing or create new)
            try:
                # Attempt to find patient by unique contact number
                patient_instance = Patient.objects.get(
                    contact_number=patient_form.cleaned_data['contact_number']
                )
                # Update details if necessary
                patient_instance.name = patient_form.cleaned_data['name']
                patient_instance.age = patient_form.cleaned_data['age']
                patient_instance.save()
            except Patient.DoesNotExist:
                # If patient does not exist, save the new patient form
                patient_instance = patient_form.save()
            
            # 2. Handle Booking
            booking_instance = booking_form.save(commit=False) # Don't save yet
            booking_instance.patient = patient_instance        # Link the patient
            booking_instance.save()                           # Save the booking

            # Redirect to a success page or the admin list (Day 3 requirement)
            return redirect('booking_success') 
            
    context = {
        'patient_form': patient_form,
        'booking_form': booking_form,
    }
    return render(request, 'booking_app/booking.html', context)

def booking_success_view(request):
    """Placeholder view for a successful booking."""
    return render(request, 'booking_app/success.html')