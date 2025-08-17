from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subscription(models.Model):
    email = models.EmailField(unique=True, verbose_name='E-poçt Ünvanı')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='İstifadəçi')
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Abunə Tarixi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yenilənmə Tarixi')

    class Meta:
        verbose_name = 'Abunə'
        verbose_name_plural = 'Abunələr'

    def __str__(self):
        return self.email

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='Ad')
    email = models.EmailField(verbose_name='E-poçt Ünvanı')
    message = models.TextField(verbose_name='Mesaj')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Göndərilmə Tarixi')
    is_resolved = models.BooleanField(default=False, verbose_name='Həll Edilib')

    class Meta:
        verbose_name = 'Əlaqə Mesajı'
        verbose_name_plural = 'Əlaqə Mesajları'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"