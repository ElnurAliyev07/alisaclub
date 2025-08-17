from django.urls import path
from . import views

app_name = 'medals'

urlpatterns = [
    path('', views.medal_list, name='medal_list'),
    path('<int:pk>/', views.medal_detail, name='medal_detail'),
    path('my-medals/', views.user_medals, name='user_medals'),
    path('passport/<int:child_id>/', views.virtual_passport, name='virtual_passport'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('achievements/', views.achievements_list, name='achievements_list'),
    path('check-eligibility/', views.check_medal_eligibility, name='check_eligibility'),
]
