from django.urls import path
from . import views

app_name = 'kids_content'

urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('<int:pk>/', views.material_detail, name='material_detail'),
    path('<int:pk>/download/', views.download_material, name='download_material'),
    path('<int:pk>/rating/', views.add_rating, name='add_rating'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:pk>/progress/', views.update_progress, name='update_progress'),
    path('category/<int:category_id>/', views.category_materials, name='category_materials'),
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    path('my-progress/', views.my_progress, name='my_progress'),
]
