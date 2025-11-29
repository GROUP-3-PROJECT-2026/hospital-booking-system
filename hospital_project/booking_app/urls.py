# booking_app/urls.py
from django.urls import path
from . import views
from .views import AdminBookingListView

urlpatterns = [
    path('', views.book_test_view, name='book_test'),
    path('book/', views.book_test_view, name='book_test'),
    path('success/', views.booking_success_view, name='booking_success'),
    path('admin-review/', AdminBookingListView.as_view(), name='admin_booking_list'),
]