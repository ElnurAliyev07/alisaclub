from django.urls import path
from . import views

app_name = 'birthday'

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('paket/<int:pk>/', views.package_detail, name='package_detail'),
    path('rezervasiya/<int:package_id>/', views.book_birthday, name='book_birthday'),
    path('rezervasiyalarim/', views.my_bookings, name='my_bookings'),
    path('rezervasiya-detay/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('planlayici/', views.planner, name='planner'),
]