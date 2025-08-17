"""
URL configuration for alisa_club project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('membership/', include('apps.membership.urls')),
    path('events/', include('apps.events.urls')),
    path('kids/', include('apps.kids_content.urls')),
    path('medals/', include('apps.medals.urls')),
    path('birthday/', include('apps.birthday.urls')),
    path('blog/', include('apps.blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
