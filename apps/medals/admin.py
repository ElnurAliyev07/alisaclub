from django.contrib import admin
from .models import MedalCategory, Medal, UserMedal, VirtualPassport, Achievement, UserAchievement, PointHistory, Leaderboard


@admin.register(MedalCategory)
class MedalCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon', 'order']
    list_editable = ['order']
    search_fields = ['name']


@admin.register(Medal)
class MedalAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'medal_type', 'rarity', 'points', 'is_active']
    list_filter = ['category', 'medal_type', 'rarity', 'is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['required_medals']


@admin.register(UserMedal)
class UserMedalAdmin(admin.ModelAdmin):
    list_display = ['child', 'medal', 'earned_date', 'event', 'material']
    list_filter = ['earned_date', 'medal__category', 'medal__medal_type']
    search_fields = ['child__name', 'medal__name', 'user__username']
    readonly_fields = ['earned_date']


@admin.register(VirtualPassport)
class VirtualPassportAdmin(admin.ModelAdmin):
    list_display = ['child', 'passport_number', 'level', 'total_points', 'issue_date']
    list_filter = ['level', 'issue_date']
    search_fields = ['child__name', 'passport_number']
    readonly_fields = ['passport_number', 'issue_date']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'achievement_type', 'points_reward', 'is_active']
    list_filter = ['achievement_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['child', 'achievement', 'earned_date']
    list_filter = ['earned_date', 'achievement__achievement_type']
    search_fields = ['child__name', 'achievement__name']
    readonly_fields = ['earned_date']


@admin.register(PointHistory)
class PointHistoryAdmin(admin.ModelAdmin):
    list_display = ['passport', 'points', 'source', 'balance_after', 'created_at']
    list_filter = ['created_at']
    search_fields = ['passport__child__name', 'source']
    readonly_fields = ['created_at']
