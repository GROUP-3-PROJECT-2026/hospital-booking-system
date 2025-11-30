from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Patient, Test, Booking
from .forms import PatientForm, TestForm, BookingForm
import json

# --- BOOKINGS ---
def booking_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        bookings = Booking.objects.filter(
            patient__name__icontains=search_query
        ) | Booking.objects.filter(
            test__name__icontains=search_query
        )
    else:
        bookings = Booking.objects.all()
    return render(request, 'booking/bookings.html', {'bookings': bookings})

def add_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'booking/add_booking.html', {'form': form, 'form_title': 'Add Booking', 'button_text': 'Save'})

def edit_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking/edit_booking.html', {'form': form, 'form_title': 'Edit Booking', 'button_text': 'Update'})

def delete_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        return redirect('booking_list')
    return render(request, 'booking/delete_booking.html', {'object': booking})

# --- PATIENTS ---
def patient_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        patients = Patient.objects.filter(name__icontains=search_query)
    else:
        patients = Patient.objects.all()
    return render(request, 'booking/patient_list.html', {'patients': patients})

def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'booking/add_patient.html', {'form': form, 'form_title': 'Add Patient', 'button_text': 'Save'})

def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'booking/add_patient.html', {'form': form, 'form_title': 'Edit Patient', 'button_text': 'Update'})

def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('patient_list')
    return render(request, 'booking/delete_patient.html', {'object': patient})

# --- TESTS ---
@login_required
def test_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        tests = Test.objects.filter(name__icontains=search_query)
    else:
        tests = Test.objects.all()
    return render(request, 'booking/test_list.html', {'tests': tests})

@login_required
def add_test(request):
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('test_list')
    else:
        form = TestForm()
    return render(request, 'booking/add_test.html', {'form': form, 'form_title': 'Add Test', 'button_text': 'Save'})

@login_required
def edit_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            return redirect('test_list')
    else:
        form = TestForm(instance=test)
    return render(request, 'booking/edit_test.html', {'form': form, 'form_title': 'Edit Test', 'button_text': 'Update'})

@login_required
def delete_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == 'POST':
        test.delete()
        return redirect('test_list')
    return render(request, 'booking/delete_test.html', {'object': test})
from django.shortcuts import render
from .models import Booking, Patient, Test

@login_required
def admin_dashboard(request):
    # Fetch some stats or just render the dashboard for now
    total_bookings = Booking.objects.count()
    total_patients = Patient.objects.count()
    total_tests = Test.objects.count()
    
    context = {
        'total_bookings': total_bookings,
        'total_patients': total_patients,
        'total_tests': total_tests
    }
    return render(request, 'booking/admin_dashboard.html', context)

def user_home(request):
    """Simple user interface for the hospital booking system"""
    # Get some basic stats for display
    recent_bookings = Booking.objects.order_by('-date')[:5]
    available_tests = Test.objects.all()
    
    context = {
        'recent_bookings': recent_bookings,
        'available_tests': available_tests,
        'total_tests': Test.objects.count(),
        'total_patients': Patient.objects.count()
    }
    return render(request, 'booking/user_home.html', context)

# AJAX view for creating patients from booking form
@csrf_exempt
@require_http_methods(["POST"])
def create_patient_ajax(request):
    try:
        data = json.loads(request.body)
        form = PatientForm(data)
        if form.is_valid():
            patient = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Patient created successfully!',
                'patient': {
                    'id': patient.id,
                    'name': patient.name,
                    'age': patient.age,
                    'contact_number': patient.contact_number
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': form.errors
            })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data.'
        })
