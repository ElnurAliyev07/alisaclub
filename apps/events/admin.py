from django.contrib import admin
from .models import EventCategory, Event, Booking, EventReview


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon']
    search_fields = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'date', 'max_participants', 'booking_count', 'available_spots', 'status']
    list_filter = ['category', 'status', 'age_group', 'date']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def booking_count(self, obj):
        return obj.booking_count
    booking_count.short_description = 'Rezervasiya sayı'
    
    def available_spots(self, obj):
        return obj.available_spots
    available_spots.short_description = 'Boş yerlər'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['event', 'child', 'user', 'status', 'booking_date', 'attended']
    list_filter = ['status', 'attended', 'booking_date']
    search_fields = ['event__title', 'child__name', 'user__username']
    readonly_fields = ['booking_date']


@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['event__title', 'user__username', 'comment']
    readonly_fields = ['created_at']
