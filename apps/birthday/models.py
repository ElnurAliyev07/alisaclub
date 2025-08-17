from django.db import models
from django.contrib.auth.models import User
from apps.membership.models import Child
from django.utils import timezone
from datetime import timedelta

class BirthdayPackage(models.Model):
    PACKAGE_TYPES = [
        ('basic', 'Əsas Paket'),
        ('premium', 'Premium Paket'),
        ('deluxe', 'Deluxe Paket'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Paket Adı')
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES, verbose_name='Paket Növü')
    description = models.TextField(verbose_name='Təsvir')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Qiymət')
    duration_hours = models.IntegerField(verbose_name='Müddət (saat)')
    max_guests = models.IntegerField(verbose_name='Maksimum Qonaq Sayı')
    includes = models.TextField(verbose_name='Daxil Olan Xidmətlər')
    image = models.ImageField(upload_to='birthday_packages/', blank=True, verbose_name='Şəkil')
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ad Günü Paketi'
        verbose_name_plural = 'Ad Günü Paketləri'
    
    def __str__(self):
        return self.name

class BirthdayBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Gözləyir'),
        ('confirmed', 'Təsdiqləndi'),
        ('cancelled', 'Ləğv Edildi'),
        ('completed', 'Tamamlandı'),
    ]
    
    parent = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Valideyn')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, verbose_name='Uşaq')
    package = models.ForeignKey(BirthdayPackage, on_delete=models.CASCADE, verbose_name='Paket')
    booking_date = models.DateTimeField(verbose_name='Rezervasiya Tarixi')
    guest_count = models.IntegerField(verbose_name='Qonaq Sayı')
    special_requests = models.TextField(blank=True, verbose_name='Xüsusi İstəklər')
    contact_phone = models.CharField(max_length=20, verbose_name='Əlaqə Telefonu')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ümumi Qiymət')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ad Günü Rezervasiyası'
        verbose_name_plural = 'Ad Günü Rezervasiyaları'
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"{self.child.name} - {self.booking_date.strftime('%d.%m.%Y')}"
    
    def is_upcoming(self):
        return self.booking_date > timezone.now()

class BirthdayReminder(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, verbose_name='Uşaq')
    reminder_date = models.DateField(verbose_name='Xatırlatma Tarixi')
    is_sent = models.BooleanField(default=False, verbose_name='Göndərildi')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ad Günü Xatırlatması'
        verbose_name_plural = 'Ad Günü Xatırlatmaları'
    
    def __str__(self):
        return f"{self.child.name} - {self.reminder_date}"

class BirthdayInquiry(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Valideyn', null=True, blank=True)
    child_name = models.CharField(max_length=100, verbose_name='Uşağın Adı')
    child_age = models.IntegerField(verbose_name='Uşağın Yaşı')
    event_date = models.DateField(verbose_name='Doğum Günü Tarixi')
    guest_count = models.IntegerField(verbose_name='Qonaq Sayı')
    theme = models.CharField(max_length=50, choices=[
        ('superhero', 'Superqəhrəmanlar'),
        ('princess', 'Şahzadələr'),
        ('space', 'Kosmik Macəra'),
        ('jungle', 'Cəngəllik Səyahəti'),
        ('other', 'Digər'),
    ], blank=True, verbose_name='Mövzu')
    notes = models.TextField(blank=True, verbose_name='Əlavə Qeydlər')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='Əlaqə Telefonu')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ad Günü Sorğusu'
        verbose_name_plural = 'Ad Günü Sorğuları'
    
    def __str__(self):
        return f"{self.child_name} - {self.event_date}"
