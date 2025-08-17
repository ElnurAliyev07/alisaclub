from django.contrib import admin
from .models import BlogCategory, BlogPost, BlogComment

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'description', 'color', 'icon', 'is_active')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at',)
        return ()

class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 1
    fields = ('author', 'content', 'is_approved', 'created_at')
    readonly_fields = ('created_at', 'author')
    can_delete = True

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'views_count', 'published_at', 'created_at')
    list_filter = ('status', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'excerpt', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    inlines = [BlogCommentInline]
    date_hierarchy = 'published_at'
    fields = (
        'title', 'slug', 'author', 'category', 'excerpt', 
        'content', 'featured_image', 'status', 'is_featured', 
        'tags', 'read_time', 'views_count', 'published_at'
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'updated_at', 'views_count')
        return ()

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username', 'post__title')
    list_editable = ('is_approved',)
    date_hierarchy = 'created_at'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'author', 'post')
        return ()