from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('preview/', views.event_list_preview, name='event_list_preview'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/book/', views.book_event, name='book_event'),
    path('booking/<int:booking_id>/success/', views.booking_success, name='booking_success'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<int:pk>/review/', views.add_review, name='add_review'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]