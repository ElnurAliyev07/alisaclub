from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('child/add/', views.add_child, name='add_child'),
    path('child/<int:pk>/', views.child_detail, name='child_detail'),
    path('child/<int:pk>/edit/', views.edit_child, name='edit_child'),
    path('membership/', views.membership, name='membership'),
]
