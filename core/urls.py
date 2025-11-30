from django.urls import path
from core import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main Dashboard & Booking Management
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Patient Management
    path('patient/create/', views.create_patient, name='create_patient'),
    path('patient/profile/', views.patient_profile_view, name='patient_profile'),
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    
    # Booking Operations
    path('booking/create/', views.BookingListView.as_view(), name='booking_create'),  # Handled in BookingListView POST
    path('booking/<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking_update'),
    path('booking/<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('booking/<int:pk>/restore/', views.BookingRestoreView.as_view(), name='booking_restore'),
    path('booking/<int:pk>/hard-delete/', views.BookingHardDeleteView.as_view(), name='booking_hard_delete'),
    
    # Time Slot Management
    path('time-slots/', views.TimeSlotListView.as_view(), name='time_slot_list'),
    path('time-slots/generate/', views.generate_time_slots, name='generate_time_slots'),
    path('admin_settings/', views.AdminSettingsView.as_view(), name='admin_settings'),
    path('admin/maintenance/', views.system_maintenance, name='system_maintenance'),
]