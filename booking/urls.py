from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('user/', views.user_home, name='user_home'),
    path('login/', auth_views.LoginView.as_view(template_name='booking/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # AJAX endpoints
    path('ajax/create-patient/', views.create_patient_ajax, name='create_patient_ajax'),
    
    # Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/add/', views.add_booking, name='add_booking'),
    path('bookings/edit/<int:pk>/', views.edit_booking, name='edit_booking'),
    path('bookings/delete/<int:pk>/', views.delete_booking, name='delete_booking'),

    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/edit/<int:pk>/', views.edit_patient, name='edit_patient'),
    path('patients/delete/<int:pk>/', views.delete_patient, name='delete_patient'),

    # Tests
    path('tests/', views.test_list, name='test_list'),
    path('tests/add/', views.add_test, name='add_test'),
    path('tests/edit/<int:pk>/', views.edit_test, name='edit_test'),
    path('tests/delete/<int:pk>/', views.delete_test, name='delete_test'),
]
