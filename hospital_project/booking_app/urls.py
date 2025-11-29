# booking_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_test_view, name='book_test'),
    path('success/', views.booking_success_view, name='booking_success'),
]