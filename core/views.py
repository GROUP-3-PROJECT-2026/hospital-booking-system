from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from core.models import Booking, Patient, Test, UserProfile, TimeSlot
from core.forms import BookingForm, RegisterForm, LoginForm, PatientForm, BookingRestoreForm, TimeSlotForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

def admin_required(function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'ADMIN':
            messages.error(request, "Admin access required.")
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrapper

def staff_required(function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'userprofile') or request.user.userprofile.role not in ['ADMIN', 'RECEPTIONIST']:
            messages.error(request, "Staff access required.")
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrapper

# Registration View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('booking_list')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('booking_list')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get('next', 'booking_list')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

# Home/Booking List View
@method_decorator(login_required, name='dispatch')
class BookingListView(View):
    template_name = 'booking_list.html'

    def get(self, request):
        user_profile = request.user.userprofile
        form = BookingForm()
        patient_form = PatientForm()
        
        # Role-based data filtering with SOFT DELETE support
        if user_profile.role == 'PATIENT':
            # Patients only see their own ACTIVE bookings
            patient = getattr(request.user, 'patient_profile', None)
            if patient:
                bookings = Booking.objects.filter(
                    patient=patient, 
                    is_active=True
                ).select_related('patient', 'test').order_by('booking_date', 'booking_time')
            else:
                # Try legacy patient matching for backward compatibility
                try:
                    patient = Patient.objects.filter(
                        Q(email=request.user.email) | Q(contact_number=request.user.username),
                        is_active=True
                    ).first()
                    if patient:
                        bookings = Booking.objects.filter(
                            patient=patient, 
                            is_active=True
                        ).select_related('patient', 'test').order_by('booking_date', 'booking_time')
                    else:
                        bookings = Booking.objects.none()
                        messages.info(request, "No patient profile found. Please contact administration if you believe this is an error.")
                except Patient.DoesNotExist:
                    bookings = Booking.objects.none()
        else:
            # Staff see all ACTIVE bookings by default
            show_cancelled = request.GET.get('show_cancelled', 'false') == 'true'
            if show_cancelled:
                bookings = Booking.objects.select_related('patient', 'test').all().order_by('booking_date', 'booking_time')
            else:
                bookings = Booking.objects.filter(is_active=True).select_related('patient', 'test').order_by('booking_date', 'booking_time')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            bookings = bookings.filter(
                Q(patient__name__icontains=search_query) |
                Q(test__name__icontains=search_query) |
                Q(hospital_name__icontains=search_query)
            )
        
        # Get available time slots for the calendar (staff only)
        available_slots = None
        if user_profile.role in ['ADMIN', 'RECEPTIONIST']:
            available_slots = TimeSlot.objects.filter(
                is_available=True,
                slot_date__gte=timezone.now().date(),
                slot_date__lte=timezone.now().date() + timedelta(days=30)
            ).order_by('slot_date', 'slot_time')[:10]  # Show next 10 available slots
        
        context = {
            'bookings': bookings,
            'form': form,
            'patient_form': patient_form,
            'user_profile': user_profile,
            'search_query': search_query,
            'available_slots': available_slots,
            'show_cancelled': request.GET.get('show_cancelled', 'false') == 'true',
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user_profile = request.user.userprofile
        
        # Check if this is a patient creation request
        if 'create_patient' in request.POST:
            if user_profile.role in ['ADMIN', 'RECEPTIONIST']:
                patient_form = PatientForm(request.POST)
                if patient_form.is_valid():
                    patient = patient_form.save()
                    messages.success(request, f"Patient {patient.name} created successfully!")
                    return redirect('booking_list')
                else:
                    for field, errors in patient_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Patient creation error: {error}")
            else:
                messages.error(request, "Only staff can create patients.")
            return redirect('booking_list')
            
        # Handle booking creation
        if user_profile.role == 'PATIENT':
            messages.error(request, "Patients cannot create bookings directly. Please contact reception.")
            return redirect('booking_list')
            
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f"Booking created successfully for {booking.patient.name}!")
            return redirect('booking_list')
        else:
            # Handle form errors and return to page with context
            messages.error(request, "Please correct the errors below.")
            
            # Rebuild the context for error display
            bookings = Booking.objects.filter(is_active=True).select_related('patient', 'test').order_by('booking_date', 'booking_time')
            patient_form = PatientForm()
            
            context = {
                'bookings': bookings,
                'form': form,
                'patient_form': patient_form,
                'user_profile': user_profile,
                'search_query': request.GET.get('search', ''),
            }
            return render(request, self.template_name, context)

# Create Patient View (for staff)
@staff_required
def create_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Patient {patient.name} created successfully!")
            return redirect('booking_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Patient creation error: {error}")
    return redirect('booking_list')

# Update Booking View
@method_decorator(staff_required, name='dispatch')
class BookingUpdateView(View):
    template_name = 'booking_update.html'

    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        form = BookingForm(instance=booking)
        return render(request, self.template_name, {'form': form, 'booking': booking})

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            updated_booking = form.save()
            messages.success(request, "Booking updated successfully!")
            return redirect('booking_list')
        else:
            messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {'form': form, 'booking': booking})

# Soft Delete Booking View (Cancel Booking)
@method_decorator(staff_required, name='dispatch')
class BookingCancelView(View):
    template_name = 'booking_confirm_cancel.html'

    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, is_active=True)
        return render(request, self.template_name, {'booking': booking})

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, is_active=True)
        patient_name = booking.patient.name
        
        # SOFT DELETE: Mark as inactive instead of actual deletion
        booking.is_active = False
        booking.cancelled_at = timezone.now()
        booking.cancelled_by = request.user
        booking.status = 'CANCELLED'
        booking.save()
        
        messages.success(request, f"Booking for {patient_name} cancelled successfully!")
        return redirect('booking_list')

# Restore Booking View
@method_decorator(staff_required, name='dispatch')
class BookingRestoreView(View):
    template_name = 'booking_confirm_restore.html'

    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, is_active=False)
        form = BookingRestoreForm()
        return render(request, self.template_name, {'booking': booking, 'form': form})

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, is_active=False)
        form = BookingRestoreForm(request.POST)
        
        if form.is_valid():
            # Check if the time slot is still available
            if self.is_time_slot_available(booking):
                # RESTORE: Mark as active again
                booking.is_active = True
                booking.cancelled_at = None
                booking.cancelled_by = None
                booking.status = 'PENDING'
                booking.save()
                
                messages.success(request, f"Booking for {booking.patient.name} restored successfully!")
            else:
                messages.error(request, "Cannot restore booking: The time slot is no longer available.")
                return redirect('booking_list')
        else:
            messages.error(request, "Please confirm you want to restore this booking.")
            return render(request, self.template_name, {'booking': booking, 'form': form})
        
        return redirect('booking_list')
    
    def is_time_slot_available(self, booking):
        """Check if the original time slot is still available"""
        # Check for overlapping active bookings
        overlapping = Booking.objects.filter(
            hospital_name=booking.hospital_name,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            is_active=True
        ).exclude(pk=booking.pk)
        
        return not overlapping.exists()

# Admin Hard Delete View (for complete removal)
@method_decorator(admin_required, name='dispatch')
class BookingHardDeleteView(View):
    template_name = 'booking_confirm_hard_delete.html'

    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        return render(request, self.template_name, {'booking': booking})

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        patient_name = booking.patient.name
        booking.delete()  # Actual database deletion
        messages.warning(request, f"Booking for {patient_name} permanently deleted!")
        return redirect('booking_list')

# Time Slot Management View
@method_decorator(staff_required, name='dispatch')
class TimeSlotListView(View):
    template_name = 'timeslot_list.html'

    def get(self, request):
        time_slots = TimeSlot.objects.select_related('booking').order_by('slot_date', 'slot_time')
        
        # Filtering
        hospital_filter = request.GET.get('hospital', '')
        date_filter = request.GET.get('date', '')
        available_filter = request.GET.get('available', '')
        
        if hospital_filter:
            time_slots = time_slots.filter(hospital_name__icontains=hospital_filter)
        if date_filter:
            time_slots = time_slots.filter(slot_date=date_filter)
        if available_filter:
            if available_filter == 'available':
                time_slots = time_slots.filter(is_available=True)
            elif available_filter == 'booked':
                time_slots = time_slots.filter(is_available=False)
        
        context = {
            'time_slots': time_slots,
            'hospital_filter': hospital_filter,
            'date_filter': date_filter,
            'available_filter': available_filter,
        }
        return render(request, self.template_name, context)

# Generate Time Slots View
@admin_required
def generate_time_slots(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        hospital_name = request.POST.get('hospital_name')
        
        if not all([start_date, end_date, hospital_name]):
            messages.error(request, "All fields are required.")
            return redirect('time_slot_list')
        
        try:
            start = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            
            slots_created = 0
            current_date = start
            
            while current_date <= end:
                # Generate slots for each day (8:00 AM to 5:00 PM, 30-minute intervals)
                for hour in range(8, 17):
                    for minute in [0, 30]:
                        slot_time = timezone.datetime.strptime(f"{hour:02d}:{minute:02d}", '%H:%M').time()
                        
                        # Check if slot already exists
                        if not TimeSlot.objects.filter(
                            hospital_name=hospital_name,
                            slot_date=current_date,
                            slot_time=slot_time
                        ).exists():
                            TimeSlot.objects.create(
                                hospital_name=hospital_name,
                                slot_date=current_date,
                                slot_time=slot_time,
                                duration=30,
                                is_available=True
                            )
                            slots_created += 1
                
                current_date += timedelta(days=1)
            
            messages.success(request, f"Successfully created {slots_created} time slots for {hospital_name}.")
        
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    return redirect('time_slot_list')

# Patient Profile View
@login_required
def patient_profile_view(request):
    """View for patients to see and update their profile"""
    try:
        patient_profile = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.error(request, "No patient profile found.")
        return redirect('booking_list')
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('patient_profile')
    else:
        form = PatientForm(instance=patient_profile)
    
    # Get patient's bookings
    bookings = Booking.objects.filter(
        patient=patient_profile, 
        is_active=True
    ).select_related('test').order_by('booking_date', 'booking_time')
    
    context = {
        'form': form,
        'patient': patient_profile,
        'bookings': bookings,
    }
    return render(request, 'patient_profile.html', context)

# Dashboard View
@staff_required
def dashboard_view(request):
    """Staff dashboard with statistics"""
    total_patients = Patient.objects.filter(is_active=True).count()
    total_bookings = Booking.objects.filter(is_active=True).count()
    upcoming_bookings = Booking.objects.filter(
        is_active=True,
        booking_date__gte=timezone.now().date()
    ).count()
    cancelled_bookings = Booking.objects.filter(is_active=False).count()
    
    # Recent bookings
    recent_bookings = Booking.objects.filter(
        is_active=True
    ).select_related('patient', 'test').order_by('-created_at')[:5]
    
    # Popular tests
    from django.db.models import Count
    popular_tests = Test.objects.filter(
        is_active=True,
        booking__is_active=True
    ).annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')[:5]
    
    context = {
        'total_patients': total_patients,
        'total_bookings': total_bookings,
        'upcoming_bookings': upcoming_bookings,
        'cancelled_bookings': cancelled_bookings,
        'recent_bookings': recent_bookings,
        'popular_tests': popular_tests,
    }
    return render(request, 'dashboard.html', context)


# Patient List View (for staff)
@method_decorator(staff_required, name='dispatch')
class PatientListView(View):
    template_name = 'patient_list.html'

    def get(self, request):
        patients = Patient.objects.filter(is_active=True).select_related('user').order_by('name')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            patients = patients.filter(
                Q(name__icontains=search_query) |
                Q(contact_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Get booking statistics for each patient
        for patient in patients:
            patient.total_bookings = Booking.objects.filter(patient=patient).count()
            patient.upcoming_bookings = Booking.objects.filter(
                patient=patient, 
                booking_date__gte=timezone.now().date(),
                is_active=True
            ).count()
            patient.last_booking = Booking.objects.filter(patient=patient).order_by('-booking_date').first()
        
        # Use existing PatientForm
        form = PatientForm()
        
        context = {
            'patients': patients,
            'form': form,
            'search_query': search_query,
            'total_patients': patients.count(),
        }
        return render(request, self.template_name, context)

# Admin Settings View
@method_decorator(admin_required, name='dispatch')
class AdminSettingsView(View):
    template_name = 'admin_settings.html'

    def get(self, request):
        # Get system statistics for the dashboard
        total_users = User.objects.count()
        total_patients = Patient.objects.filter(is_active=True).count()
        total_bookings = Booking.objects.count()
        total_tests = Test.objects.filter(is_active=True).count()
        
        # Get user distribution by role
        user_roles = UserProfile.objects.values('role').annotate(count=Count('role'))
        
        # Get recent system activity
        recent_bookings = Booking.objects.select_related('patient', 'test').order_by('-created_at')[:10]
        recent_patients = Patient.objects.filter(is_active=True).order_by('-created_at')[:5]
        
        context = {
            'total_users': total_users,
            'total_patients': total_patients,
            'total_bookings': total_bookings,
            'total_tests': total_tests,
            'user_roles': user_roles,
            'recent_bookings': recent_bookings,
            'recent_patients': recent_patients,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # Handle different setting actions
        action = request.POST.get('action')
        
        if action == 'clear_old_slots':
            # Clear time slots older than today
            deleted_count = TimeSlot.objects.filter(
                slot_date__lt=timezone.now().date()
            ).delete()[0]
            messages.success(request, f"Cleared {deleted_count} old time slots.")
            
        elif action == 'generate_sample_data':
            # Generate sample test data
            sample_tests = [
                {'name': 'Blood Test', 'description': 'Complete blood count analysis', 'duration': 15},
                {'name': 'X-Ray', 'description': 'Chest X-ray examination', 'duration': 30},
                {'name': 'MRI Scan', 'description': 'Magnetic Resonance Imaging', 'duration': 60},
                {'name': 'Ultrasound', 'description': 'Abdominal ultrasound scan', 'duration': 45},
                {'name': 'ECG', 'description': 'Electrocardiogram test', 'duration': 20},
            ]
            
            created_count = 0
            for test_data in sample_tests:
                if not Test.objects.filter(name=test_data['name']).exists():
                    Test.objects.create(**test_data)
                    created_count += 1
            
            messages.success(request, f"Created {created_count} sample tests.")
            
        elif action == 'update_system_settings':
            # Handle system settings updates
            max_booking_days = request.POST.get('max_booking_days', 30)
            business_hours_start = request.POST.get('business_hours_start', '08:00')
            business_hours_end = request.POST.get('business_hours_end', '17:00')
            
            # In a real system, you'd save these to a settings model
            messages.success(request, "System settings updated successfully.")
            
        return redirect('admin_settings')

# System Maintenance Actions
@admin_required
def system_maintenance(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'cleanup_cancelled_bookings':
            # Permanently delete cancelled bookings older than 30 days
            cutoff_date = timezone.now() - timedelta(days=30)
            deleted_count = Booking.objects.filter(
                is_active=False,
                cancelled_at__lt=cutoff_date
            ).delete()[0]
            messages.success(request, f"Cleaned up {deleted_count} old cancelled bookings.")
            
        elif action == 'regenerate_next_month_slots':
            # Regenerate time slots for next month
            start_date = timezone.now().date() + timedelta(days=31)
            end_date = start_date + timedelta(days=30)
            
            hospitals = TimeSlot.objects.values_list('hospital_name', flat=True).distinct()
            slots_created = 0
            
            for hospital in hospitals:
                current_date = start_date
                while current_date <= end_date:
                    for hour in range(8, 17):
                        for minute in [0, 30]:
                            slot_time = timezone.datetime.strptime(f"{hour:02d}:{minute:02d}", '%H:%M').time()
                            
                            if not TimeSlot.objects.filter(
                                hospital_name=hospital,
                                slot_date=current_date,
                                slot_time=slot_time
                            ).exists():
                                TimeSlot.objects.create(
                                    hospital_name=hospital,
                                    slot_date=current_date,
                                    slot_time=slot_time,
                                    duration=30,
                                    is_available=True
                                )
                                slots_created += 1
                    
                    current_date += timedelta(days=1)
            
            messages.success(request, f"Generated {slots_created} time slots for next month.")
            
        elif action == 'export_system_data':
            # This would typically generate and serve a CSV file
            # For now, just show a message
            messages.info(request, "Data export feature coming soon.")
            
    return redirect('admin_settings')