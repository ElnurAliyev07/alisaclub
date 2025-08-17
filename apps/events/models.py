from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from apps.membership.models import Child


class EventCategory(models.Model):
    """Tədbir kateqoriyaları"""
    name = models.CharField(max_length=100, verbose_name='Kateqoriya adı')
    description = models.TextField(blank=True, verbose_name='Təsvir')
    color = models.CharField(max_length=7, default='#059669', verbose_name='Rəng')
    icon = models.CharField(max_length=50, default='fas fa-calendar', verbose_name='İkon')
    
    class Meta:
        verbose_name = 'Tədbir Kateqoriyası'
        verbose_name_plural = 'Tədbir Kateqoriyaları'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Event(models.Model):
    """Tədbir modeli"""
    AGE_GROUP_CHOICES = [
        ('0-3', '0-3 yaş'),
        ('3-6', '3-6 yaş'),
        ('6-9', '6-9 yaş'),
        ('9-12', '9-12 yaş'),
        ('12+', '12+ yaş'),
        ('all', 'Bütün yaşlar'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Gələcək'),
        ('ongoing', 'Davam edir'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'Ləğv edildi'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Başlıq')
    description = models.TextField(verbose_name='Təsvir')
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, related_name='events', verbose_name='Kateqoriya')
    image = models.ImageField(upload_to='events/', verbose_name='Şəkil')
    date = models.DateTimeField(verbose_name='Tarix və vaxt')
    duration = models.IntegerField(help_text='Dəqiqə ilə', verbose_name='Müddət')
    location = models.CharField(max_length=200, verbose_name='Yer')
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES, verbose_name='Yaş qrupu')
    max_participants = models.IntegerField(verbose_name='Maksimum iştirakçı sayı')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Qiymət')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name='Status')
    requirements = models.TextField(blank=True, verbose_name='Tələblər')
    what_to_bring = models.TextField(blank=True, verbose_name='Nə gətirmək lazımdır')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tədbir'
        verbose_name_plural = 'Tədbirlər'
        ordering = ['-date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})
    
    @property
    def available_spots(self):
        return self.max_participants - self.bookings.filter(status='confirmed').count()
    
    @property
    def is_full(self):
        return self.available_spots <= 0
    
    @property
    def booking_count(self):
        return self.bookings.filter(status='confirmed').count()


class Booking(models.Model):
    """Rezervasiya modeli"""
    STATUS_CHOICES = [
        ('pending', 'Gözləyir'),
        ('confirmed', 'Təsdiqləndi'),
        ('cancelled', 'Ləğv edildi'),
        ('completed', 'Tamamlandı'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings', verbose_name='Tədbir')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name='İstifadəçi')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='bookings', verbose_name='Uşaq')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name='Rezervasiya tarixi')
    notes = models.TextField(blank=True, verbose_name='Qeydlər')
    attended = models.BooleanField(default=False, verbose_name='İştirak etdi')
    
    class Meta:
        verbose_name = 'Rezervasiya'
        verbose_name_plural = 'Rezervasiyalar'
        unique_together = ['event', 'child']
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"{self.child.name} - {self.event.title}"
    
    @property
    def can_cancel(self):
        from django.utils import timezone
        return self.status in ['pending', 'confirmed'] and self.event.date > timezone.now()


class EventReview(models.Model):
    """Tədbir rəyləri"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews', verbose_name='Tədbir')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='İstifadəçi')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='Qiymət')
    comment = models.TextField(verbose_name='Şərh')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tədbir Rəyi'
        verbose_name_plural = 'Tədbir Rəyləri'
        unique_together = ['event', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.event.title} ({self.rating}/5)"
