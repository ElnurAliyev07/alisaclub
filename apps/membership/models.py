from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class MemberProfile(models.Model):
    """Valideyn profili"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    address = models.TextField(verbose_name='Ünvan')
    emergency_contact = models.CharField(max_length=100, verbose_name='Təcili əlaqə şəxsi')
    emergency_phone = models.CharField(max_length=20, verbose_name='Təcili əlaqə telefonu')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Üzv Profili'
        verbose_name_plural = 'Üzv Profilləri'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Child(models.Model):
    """Uşaq məlumatları"""
    GENDER_CHOICES = [
        ('M', 'Oğlan'),
        ('F', 'Qız'),
    ]
    
    parent = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100, verbose_name='Ad')
    surname = models.CharField(max_length=100, verbose_name='Soyad')
    birth_date = models.DateField(verbose_name='Doğum tarixi')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Cins')
    allergies = models.TextField(blank=True, verbose_name='Allergiyalar')
    special_notes = models.TextField(blank=True, verbose_name='Xüsusi qeydlər')
    photo = models.ImageField(upload_to='children_photos/', blank=True, verbose_name='Şəkil')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Uşaq'
        verbose_name_plural = 'Uşaqlar'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} {self.surname}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def get_absolute_url(self):
        return reverse('membership:child_detail', kwargs={'pk': self.pk})


class Membership(models.Model):
    """Üzvlük məlumatları"""
    MEMBERSHIP_TYPES = [
        ('basic', 'Əsas'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktiv'),
        ('inactive', 'Qeyri-aktiv'),
        ('suspended', 'Dayandırılmış'),
    ]
    
    profile = models.OneToOneField(MemberProfile, on_delete=models.CASCADE, related_name='membership')
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPES, default='basic', verbose_name='Üzvlük növü')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Status')
    start_date = models.DateField(auto_now_add=True, verbose_name='Başlama tarixi')
    end_date = models.DateField(null=True, blank=True, verbose_name='Bitmə tarixi')
    discount_percentage = models.IntegerField(default=0, verbose_name='Endirim faizi')
    
    class Meta:
        verbose_name = 'Üzvlük'
        verbose_name_plural = 'Üzvlüklər'
    
    def __str__(self):
        return f"{self.profile} - {self.get_membership_type_display()}"
    
    @property
    def is_active(self):
        return self.status == 'active'
