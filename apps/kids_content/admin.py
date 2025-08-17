from django.contrib import admin
from .models import ContentCategory, KidsMaterial, MaterialRating, Favorite, LearningProgress, MaterialDownload


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon', 'order']
    list_editable = ['order']
    search_fields = ['name']


@admin.register(KidsMaterial)
class KidsMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'material_type', 'age_group', 'difficulty_level', 'is_premium', 'is_featured', 'view_count', 'download_count']
    list_filter = ['category', 'material_type', 'age_group', 'difficulty_level', 'is_premium', 'is_featured']
    search_fields = ['title', 'description']
    readonly_fields = ['view_count', 'download_count', 'created_at', 'updated_at']
    list_editable = ['is_featured', 'is_premium']


@admin.register(MaterialRating)
class MaterialRatingAdmin(admin.ModelAdmin):
    list_display = ['material', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['material__title', 'user__username']
    readonly_fields = ['created_at']


@admin.register(MaterialDownload)
class MaterialDownloadAdmin(admin.ModelAdmin):
    list_display = ['material', 'user', 'downloaded_at', 'ip_address']
    list_filter = ['downloaded_at']
    search_fields = ['material__title', 'user__username']
    readonly_fields = ['downloaded_at']


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ['material', 'user', 'status', 'progress_percentage', 'last_accessed']
    list_filter = ['status', 'last_accessed']
    search_fields = ['material__title', 'user__username']
