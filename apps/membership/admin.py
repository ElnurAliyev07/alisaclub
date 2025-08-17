from django.contrib import admin
from .models import MemberProfile, Child, Membership


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'surname', 'parent', 'birth_date', 'age', 'gender']
    list_filter = ['gender', 'birth_date', 'created_at']
    search_fields = ['name', 'surname', 'parent__user__username']
    readonly_fields = ['created_at']
    
    def age(self, obj):
        return obj.age
    age.short_description = 'Yaş'


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['profile', 'membership_type', 'status', 'start_date', 'discount_percentage']
    list_filter = ['membership_type', 'status', 'start_date']
    search_fields = ['profile__user__username', 'profile__user__first_name']
