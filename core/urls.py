from django.urls import path
from core import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('bookings/', views.list_bookings, name='list_bookings'),
    path('bookings/new/', views.create_booking, name='create_booking'),
    path('bookings/update/<int:id>/', views.update_booking, name='update_booking'),
    path('bookings/delete/<int:id>/', views.delete_booking, name='delete_booking'),
]

