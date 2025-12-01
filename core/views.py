from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from core.models import Booking, Test
from core.forms import BookingForm


@login_required
def dashboard(request):
    """User dashboard displaying user's bookings."""
    bookings = Booking.objects.filter(user=request.user).select_related('patient', 'test')
    context = {
        'bookings': bookings,
        'user': request.user
    }
    return render(request, 'core/dashboard.html', context)


@login_required
@staff_member_required
def admin_dashboard(request):
    """Admin dashboard displaying all bookings with search functionality."""
    bookings = Booking.objects.all().select_related('patient', 'test', 'user')
    search_query = request.GET.get('search', '')
    
    if search_query:
        bookings = bookings.filter(
            Q(patient__name__icontains=search_query) |
            Q(test__name__icontains=search_query)
        )
    
    context = {
        'bookings': bookings,
        'search_query': search_query
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required
def create_booking(request):
    """Create a new booking."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('list_bookings')
    else:
        form = BookingForm()
    
    return render(request, 'core/booking_form.html', {'form': form, 'title': 'Create Booking'})


@login_required
def list_bookings(request):
    """List all bookings for the current user."""
    bookings = Booking.objects.filter(user=request.user).select_related('patient', 'test')
    context = {
        'bookings': bookings
    }
    return render(request, 'core/booking_list.html', context)


@login_required
def update_booking(request, id):
    """Update an existing booking."""
    booking = get_object_or_404(Booking, pk=id, user=request.user)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('list_bookings')
    else:
        # Pre-populate form with booking data
        form = BookingForm(initial={
            'patient_name': booking.patient.name,
            'age': booking.patient.age,
            'contact': booking.patient.contact,
            'test': booking.test,
            'date': booking.date,
            'time': booking.time,
            'hospital': booking.hospital
        })
        form.instance = booking
    
    return render(request, 'core/booking_form.html', {'form': form, 'title': 'Update Booking', 'booking': booking})


@login_required
def delete_booking(request, id):
    """Delete a booking."""
    booking = get_object_or_404(Booking, pk=id, user=request.user)
    
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return redirect('list_bookings')
    
    return render(request, 'core/booking_confirm_delete.html', {'booking': booking})
