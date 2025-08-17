from django.db import models
from django.contrib.auth.models import User
from apps.membership.models import Child
from apps.events.models import Event
from apps.kids_content.models import KidsMaterial


class MedalCategory(models.Model):
    """Medal kateqoriyaları"""
    name = models.CharField(max_length=100, verbose_name='Kateqoriya adı')
    description = models.TextField(blank=True, verbose_name='Təsvir')
    color = models.CharField(max_length=7, default='#FFD700', verbose_name='Rəng')
    icon = models.CharField(max_length=50, default='fas fa-medal', verbose_name='İkon')
    order = models.IntegerField(default=0, verbose_name='Sıralama')
    
    class Meta:
        verbose_name = 'Medal Kateqoriyası'
        verbose_name_plural = 'Medal Kateqoriyaları'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Medal(models.Model):
    """Medal modeli"""
    MEDAL_TYPES = [
        ('bronze', 'Bürünc'),
        ('silver', 'Gümüş'),
        ('gold', 'Qızıl'),
        ('platinum', 'Platin'),
        ('special', 'Xüsusi'),
    ]
    
    RARITY_LEVELS = [
        ('common', 'Adi'),
        ('uncommon', 'Nadir'),
        ('rare', 'Çox Nadir'),
        ('epic', 'Epik'),
        ('legendary', 'Əfsanəvi'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Medal adı')
    description = models.TextField(verbose_name='Təsvir')
    category = models.ForeignKey(MedalCategory, on_delete=models.CASCADE, related_name='medals', verbose_name='Kateqoriya')
    medal_type = models.CharField(max_length=20, choices=MEDAL_TYPES, verbose_name='Medal növü')
    rarity = models.CharField(max_length=20, choices=RARITY_LEVELS, default='common', verbose_name='Nadirlik')
    icon = models.CharField(max_length=50, default='fas fa-medal', verbose_name='İkon')
    image = models.ImageField(upload_to='medals/', blank=True, verbose_name='Şəkil')
    points = models.IntegerField(default=10, verbose_name='Xal')
    
    # Əldə etmə şərtləri
    required_events = models.IntegerField(default=0, verbose_name='Tələb olunan tədbir sayı')
    required_materials = models.IntegerField(default=0, verbose_name='Tələb olunan material sayı')
    required_points = models.IntegerField(default=0, verbose_name='Tələb olunan xal')
    required_medals = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name='Tələb olunan medallər')
    
    # Endirim və mükafatlar
    discount_percentage = models.IntegerField(default=0, verbose_name='Endirim faizi')
    special_privileges = models.TextField(blank=True, verbose_name='Xüsusi imtiyazlar')
    
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Medal'
        verbose_name_plural = 'Medallər'
        ordering = ['category', 'medal_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_medal_type_display()})"
    
    @property
    def color_class(self):
        colors = {
            'bronze': 'text-warning',
            'silver': 'text-secondary',
            'gold': 'text-warning',
            'platinum': 'text-info',
            'special': 'text-primary'
        }
        return colors.get(self.medal_type, 'text-muted')
    
    @property
    def rarity_color(self):
        colors = {
            'common': '#6c757d',
            'uncommon': '#28a745',
            'rare': '#007bff',
            'epic': '#6f42c1',
            'legendary': '#fd7e14'
        }
        return colors.get(self.rarity, '#6c757d')


class UserMedal(models.Model):
    """İstifadəçi medalları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_medals', verbose_name='İstifadəçi')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='medals', verbose_name='Uşaq')
    medal = models.ForeignKey(Medal, on_delete=models.CASCADE, related_name='awarded_to', verbose_name='Medal')
    earned_date = models.DateTimeField(auto_now_add=True, verbose_name='Qazanma tarixi')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Tədbir')
    material = models.ForeignKey(KidsMaterial, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Material')
    notes = models.TextField(blank=True, verbose_name='Qeydlər')
    
    class Meta:
        verbose_name = 'İstifadəçi Medalı'
        verbose_name_plural = 'İstifadəçi Medalları'
        unique_together = ['child', 'medal']
        ordering = ['-earned_date']
    
    def __str__(self):
        return f"{self.child.name} - {self.medal.name}"


class VirtualPassport(models.Model):
    """Virtual pasport"""
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='passport', verbose_name='Uşaq')
    passport_number = models.CharField(max_length=20, unique=True, verbose_name='Pasport nömrəsi')
    issue_date = models.DateTimeField(auto_now_add=True, verbose_name='Verilmə tarixi')
    total_points = models.IntegerField(default=0, verbose_name='Ümumi xal')
    level = models.IntegerField(default=1, verbose_name='Səviyyə')
    experience_points = models.IntegerField(default=0, verbose_name='Təcrübə xalı')
    
    class Meta:
        verbose_name = 'Virtual Pasport'
        verbose_name_plural = 'Virtual Pasportlar'
        ordering = ['-total_points']
    
    def __str__(self):
        return f"{self.child.name} - Pasport #{self.passport_number}"
    
    def save(self, *args, **kwargs):
        if not self.passport_number:
            # Unikal pasport nömrəsi yaradırıq
            import random
            import string
            while True:
                number = 'AC' + ''.join(random.choices(string.digits, k=6))
                if not VirtualPassport.objects.filter(passport_number=number).exists():
                    self.passport_number = number
                    break
        super().save(*args, **kwargs)
    
    def calculate_level(self):
        """Səviyyəni hesabla"""
        # Hər 100 xal üçün 1 səviyyə
        new_level = max(1, self.total_points // 100)
        if new_level != self.level:
            self.level = new_level
            self.save(update_fields=['level'])
        return self.level
    
    def add_points(self, points, source=None):
        """Xal əlavə et"""
        self.total_points += points
        self.experience_points += points
        self.calculate_level()
        self.save(update_fields=['total_points', 'experience_points'])
        
        # Xal qeydini yarat
        PointHistory.objects.create(
            passport=self,
            points=points,
            source=source or 'Manual',
            balance_after=self.total_points
        )
    
    @property
    def medal_count(self):
        return self.child.medals.count()
    
    @property
    def bronze_medals(self):
        return self.child.medals.filter(medal__medal_type='bronze').count()
    
    @property
    def silver_medals(self):
        return self.child.medals.filter(medal__medal_type='silver').count()
    
    @property
    def gold_medals(self):
        return self.child.medals.filter(medal__medal_type='gold').count()
    
    @property
    def next_level_points(self):
        return (self.level * 100) - self.total_points + 100


class PointHistory(models.Model):
    """Xal tarixçəsi"""
    passport = models.ForeignKey(VirtualPassport, on_delete=models.CASCADE, related_name='point_history', verbose_name='Pasport')
    points = models.IntegerField(verbose_name='Xal')
    source = models.CharField(max_length=200, verbose_name='Mənbə')
    balance_after = models.IntegerField(verbose_name='Sonrakı balans')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Xal Tarixçəsi'
        verbose_name_plural = 'Xal Tarixçələri'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.passport.child.name} - {self.points} xal ({self.source})"


class Achievement(models.Model):
    """Nailiyyətlər"""
    ACHIEVEMENT_TYPES = [
        ('event_participation', 'Tədbir İştirakı'),
        ('material_completion', 'Material Tamamlama'),
        ('medal_collection', 'Medal Toplama'),
        ('streak', 'Ardıcıllıq'),
        ('special', 'Xüsusi'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nailiyyət adı')
    description = models.TextField(verbose_name='Təsvir')
    achievement_type = models.CharField(max_length=30, choices=ACHIEVEMENT_TYPES, verbose_name='Nailiyyət növü')
    icon = models.CharField(max_length=50, default='fas fa-trophy', verbose_name='İkon')
    color = models.CharField(max_length=7, default='#FFD700', verbose_name='Rəng')
    points_reward = models.IntegerField(default=50, verbose_name='Xal mükafatı')
    
    # Şərtlər
    required_count = models.IntegerField(default=1, verbose_name='Tələb olunan say')
    required_days = models.IntegerField(default=0, verbose_name='Tələb olunan gün')
    
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Nailiyyət'
        verbose_name_plural = 'Nailiyyətlər'
        ordering = ['achievement_type', 'name']
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """İstifadəçi nailiyyətləri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements', verbose_name='İstifadəçi')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='achievements', verbose_name='Uşaq')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='earned_by', verbose_name='Nailiyyət')
    earned_date = models.DateTimeField(auto_now_add=True, verbose_name='Qazanma tarixi')
    
    class Meta:
        verbose_name = 'İstifadəçi Nailiyyəti'
        verbose_name_plural = 'İstifadəçi Nailiyyətləri'
        unique_together = ['child', 'achievement']
        ordering = ['-earned_date']
    
    def __str__(self):
        return f"{self.child.name} - {self.achievement.name}"


class Leaderboard(models.Model):
    """Liderlik cədvəli"""
    PERIOD_CHOICES = [
        ('weekly', 'Həftəlik'),
        ('monthly', 'Aylıq'),
        ('yearly', 'İllik'),
        ('all_time', 'Bütün vaxtlar'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, verbose_name='Uşaq')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, verbose_name='Dövr')
    points = models.IntegerField(verbose_name='Xal')
    rank = models.IntegerField(verbose_name='Rəqəm')
    period_start = models.DateField(verbose_name='Dövr başlanğıcı')
    period_end = models.DateField(verbose_name='Dövr sonu')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Liderlik Cədvəli'
        verbose_name_plural = 'Liderlik Cədvəlləri'
        unique_together = ['child', 'period', 'period_start']
        ordering = ['period', 'rank']
    
    def __str__(self):
        return f"{self.child.name} - {self.get_period_display()} #{self.rank}"
