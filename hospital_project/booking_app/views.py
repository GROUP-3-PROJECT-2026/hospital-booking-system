# booking_app/views.py
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import PatientForm, BookingForm
from .models import Patient, Booking, TestCatalogue
from django.db.models import Q # For complex queries
from django.views.generic import ListView
from django.db import IntegrityError

@require_http_methods(["GET", "POST"])
def book_test_view(request):
    # Initialize forms with POST data or None
    patient_form = PatientForm(request.POST or None)
    booking_form = BookingForm(request.POST or None)

    if request.method == 'POST':
        if patient_form.is_valid() and booking_form.is_valid():
            
            # 1. Handle Patient (find existing or create new)
            contact_num = patient_form.cleaned_data['contact_number']
            try:
                # Attempt to find patient by unique contact number
                patient_instance = Patient.objects.get(contact_number=contact_num)
                # Update details if necessary
                patient_instance.name = patient_form.cleaned_data['name']
                patient_instance.age = patient_form.cleaned_data['age']
                patient_instance.save()
            except Patient.DoesNotExist:
                # If patient does not exist, save the new patient form
                patient_instance = patient_form.save()
            
            # --- 🌟 CORE DAY 3 LOGIC: DUPLICATE CHECK ---
            submitted_test = booking_form.cleaned_data['test']
            submitted_date = booking_form.cleaned_data['booking_date']
            submitted_time = booking_form.cleaned_data['booking_time']
            
            # Check for existing booking based on the four critical fields
            is_duplicate = Booking.objects.filter(
                patient=patient_instance,
                test=submitted_test,
                booking_date=submitted_date,
                booking_time=submitted_time,
            ).exists()
            
            if is_duplicate:
                # Add a non-field error to the booking form and stop processing
                error_message = "ERROR: A duplicate booking already exists for this patient, test, date, and time. Please select another slot."
                booking_form.add_error(None, error_message)
            else:
                # 2. Handle Booking (If unique)
                try:
                    booking_instance = booking_form.save(commit=False) # Don't save yet
                    booking_instance.patient = patient_instance        # Link the patient
                    booking_instance.save()                           # Save the booking
                    
                    # Redirect to success page
                    return redirect('booking_success') 
                except IntegrityError:
                    # Catch the unlikely race condition where two identical submissions happen simultaneously
                    booking_form.add_error(None, "System Error: Failed to save booking due to a concurrency issue. Please try again.")

    context = {
        'patient_form': patient_form,
        'booking_form': booking_form,
    }
    return render(request, 'booking_app/booking.html', context)

class AdminBookingListView(ListView):
    """
    Displays all submitted bookings in a structured table.
    Supports searching by Patient Name or Test Type.
    """
    model = Booking
    template_name = 'booking_app/admin_list.html'
    context_object_name = 'bookings'
    # Order by date/time ascending by default
    ordering = ['booking_date', 'booking_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Implement Filtering/Searching based on URL parameter 'q'
        query = self.request.GET.get('q')
        if query:
            # Use Q object for OR logic (Search by Patient Name OR Test Name)
            queryset = queryset.filter(
                Q(patient__name__icontains=query) | # Search Patient Name (case-insensitive)
                Q(test__test_name__icontains=query)  # Search Test Type (case-insensitive)
            )
        return queryset

def booking_success_view(request):
    """Placeholder view for a successful booking."""
    return render(request, 'booking_app/success.html')