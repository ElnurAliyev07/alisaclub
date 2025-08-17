from django.contrib import admin
from .models import Subscription, ContactMessage

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'user__username', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('email', 'user', 'is_active')
        }),
        ('Tarixçə', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['deactivate_subscriptions', 'activate_subscriptions']
    ordering = ('-created_at',)

    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, 'Seçilmiş abunələr deaktiv edildi.')
    deactivate_subscriptions.short_description = 'Seçilmiş abunələri deaktiv et'

    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, 'Seçilmiş abunələr aktiv edildi.')
    activate_subscriptions.short_description = 'Seçilmiş abunələri aktiv et'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'message', 'is_resolved')
        }),
        ('Tarixçə', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_resolved', 'mark_unresolved']
    ordering = ('-created_at',)

    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, 'Seçilmiş mesajlar həll edilmiş kimi qeyd olundu.')
    mark_resolved.short_description = 'Seçilmiş mesajları həll edilmiş kimi qeyd et'

    def mark_unresolved(self, request, queryset):
        queryset.update(is_resolved=False)
        self.message_user(request, 'Seçilmiş mesajlar həll edilməmiş kimi qeyd olundu.')
    mark_unresolved.short_description = 'Seçilmiş mesajları həll edilməmiş kimi qeyd et'