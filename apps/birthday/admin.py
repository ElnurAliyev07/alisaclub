from django.contrib import admin
from .models import BirthdayPackage, BirthdayBooking, BirthdayReminder

@admin.register(BirthdayPackage)
class BirthdayPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_type', 'price', 'duration_hours', 'max_guests', 'is_active')
    list_filter = ('package_type', 'is_active')
    search_fields = ('name', 'description', 'includes')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'package_type', 'price', 'duration_hours', 'max_guests', 'is_active')
        }),
        ('Təsvir və Xidmətlər', {
            'fields': ('description', 'includes')
        }),
        ('Şəkil', {
            'fields': ('image',)
        }),
        ('Tarixçə', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['deactivate_packages', 'activate_packages']
    ordering = ('price',)

    def deactivate_packages(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, 'Seçilmiş paketlər deaktiv edildi.')
    deactivate_packages.short_description = 'Seçilmiş paketləri deaktiv et'

    def activate_packages(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, 'Seçilmiş paketlər aktiv edildi.')
    activate_packages.short_description = 'Seçilmiş paketləri aktiv et'

@admin.register(BirthdayBooking)
class BirthdayBookingAdmin(admin.ModelAdmin):
    list_display = ('child', 'parent', 'package', 'booking_date', 'guest_count', 'status', 'total_price')
    list_filter = ('status', 'booking_date')
    search_fields = ('child__name', 'parent__username', 'package__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('parent', 'child', 'package', 'booking_date', 'guest_count', 'status', 'total_price')
        }),
        ('Əlavə Məlumat', {
            'fields': ('special_requests', 'contact_phone')
        }),
        ('Tarixçə', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_confirmed', 'mark_cancelled', 'mark_completed']
    ordering = ('-booking_date',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent', 'child', 'package')

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, 'Seçilmiş rezervasiyalar təsdiqləndi.')
    mark_confirmed.short_description = 'Seçilmiş rezervasiyaları təsdiqlə'

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, 'Seçilmiş rezervasiyalar ləğv edildi.')
    mark_cancelled.short_description = 'Seçilmiş rezervasiyaları ləğv et'

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, 'Seçilmiş rezervasiyalar tamamlandı.')
    mark_completed.short_description = 'Seçilmiş rezervasiyaları tamamla'

@admin.register(BirthdayReminder)
class BirthdayReminderAdmin(admin.ModelAdmin):
    list_display = ('child', 'reminder_date', 'is_sent', 'created_at')
    list_filter = ('is_sent', 'reminder_date')
    search_fields = ('child__name', 'child__surname')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('child', 'reminder_date', 'is_sent')
        }),
        ('Tarixçə', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_sent', 'mark_not_sent']
    ordering = ('-reminder_date',)

    def mark_sent(self, request, queryset):
        queryset.update(is_sent=True)
        self.message_user(request, 'Seçilmiş xatırlatmalar göndərilmiş kimi qeyd olundu.')
    mark_sent.short_description = 'Seçilmiş xatırlatmaları göndərilmiş kimi qeyd et'

    def mark_not_sent(self, request, queryset):
        queryset.update(is_sent=False)
        self.message_user(request, 'Seçilmiş xatırlatmalar göndərilməmiş kimi qeyd olundu.')
    mark_not_sent.short_description = 'Seçilmiş xatırlatmaları göndərilməmiş kimi qeyd et'