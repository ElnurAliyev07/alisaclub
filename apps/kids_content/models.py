from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class ContentCategory(models.Model):
    """Məzmun kateqoriyaları"""
    name = models.CharField(max_length=100, verbose_name='Kateqoriya adı')
    description = models.TextField(blank=True, verbose_name='Təsvir')
    color = models.CharField(max_length=7, default='#10b981', verbose_name='Rəng')
    icon = models.CharField(max_length=50, default='fas fa-book', verbose_name='İkon')
    order = models.IntegerField(default=0, verbose_name='Sıralama')
    
    class Meta:
        verbose_name = 'Məzmun Kateqoriyası'
        verbose_name_plural = 'Məzmun Kateqoriyaları'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class KidsMaterial(models.Model):
    """Uşaq materialları"""
    MATERIAL_TYPES = [
        ('pdf', 'PDF Fayl'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('game', 'Oyun'),
        ('coloring', 'Rəngləmə Səhifəsi'),
        ('story', 'Nağıl'),
        ('activity', 'Fəaliyyət'),
        ('worksheet', 'İş Vərəqi'),
    ]
    
    AGE_GROUPS = [
        ('0-3', '0-3 yaş'),
        ('3-6', '3-6 yaş'),
        ('6-9', '6-9 yaş'),
        ('9-12', '9-12 yaş'),
        ('12+', '12+ yaş'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Asan'),
        ('medium', 'Orta'),
        ('hard', 'Çətin'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Başlıq')
    description = models.TextField(verbose_name='Təsvir')
    category = models.ForeignKey(ContentCategory, on_delete=models.CASCADE, related_name='materials', verbose_name='Kateqoriya')
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, verbose_name='Material növü')
    age_group = models.CharField(max_length=10, choices=AGE_GROUPS, verbose_name='Yaş qrupu')
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='easy', verbose_name='Çətinlik səviyyəsi')
    
    # Fayl sahələri
    file = models.FileField(upload_to='kids_materials/', blank=True, verbose_name='Fayl')
    image = models.ImageField(upload_to='kids_materials/images/', blank=True, verbose_name='Şəkil')
    video_url = models.URLField(blank=True, verbose_name='Video URL')
    
    # Məzmun sahələri
    content = models.TextField(blank=True, verbose_name='Məzmun')
    instructions = models.TextField(blank=True, verbose_name='Təlimatlar')
    learning_objectives = models.TextField(blank=True, verbose_name='Öyrənmə məqsədləri')
    
    # Metadata
    duration_minutes = models.IntegerField(blank=True, null=True, verbose_name='Müddət (dəqiqə)')
    is_premium = models.BooleanField(default=False, verbose_name='Premium məzmun')
    is_featured = models.BooleanField(default=False, verbose_name='Seçilmiş məzmun')
    download_count = models.IntegerField(default=0, verbose_name='Yükləmə sayı')
    view_count = models.IntegerField(default=0, verbose_name='Baxış sayı')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Uşaq Materialı'
        verbose_name_plural = 'Uşaq Materialları'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('kids_content:material_detail', kwargs={'pk': self.pk})
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])


class MaterialRating(models.Model):
    """Material qiymətləndirmələri"""
    material = models.ForeignKey(KidsMaterial, on_delete=models.CASCADE, related_name='ratings', verbose_name='Material')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='İstifadəçi')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='Qiymət')
    comment = models.TextField(blank=True, verbose_name='Şərh')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Material Qiyməti'
        verbose_name_plural = 'Material Qiymətləri'
        unique_together = ['material', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.material.title} ({self.rating}/5)"


class MaterialDownload(models.Model):
    """Material yükləmələri"""
    material = models.ForeignKey(KidsMaterial, on_delete=models.CASCADE, related_name='downloads', verbose_name='Material')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='İstifadəçi')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Material Yükləməsi'
        verbose_name_plural = 'Material Yükləmələri'
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.material.title}"


class Favorite(models.Model):
    """Sevimli materiallar"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='İstifadəçi')
    material = models.ForeignKey(KidsMaterial, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Material')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sevimli'
        verbose_name_plural = 'Sevimlilər'
        unique_together = ['user', 'material']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.material.title}"


class LearningProgress(models.Model):
    """Öyrənmə tərəqqisi"""
    STATUS_CHOICES = [
        ('not_started', 'Başlanmayıb'),
        ('in_progress', 'Davam edir'),
        ('completed', 'Tamamlandı'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_progress', verbose_name='İstifadəçi')
    material = models.ForeignKey(KidsMaterial, on_delete=models.CASCADE, related_name='progress_records', verbose_name='Material')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name='Status')
    progress_percentage = models.IntegerField(default=0, verbose_name='Tərəqqi faizi')
    time_spent_minutes = models.IntegerField(default=0, verbose_name='Sərf edilən vaxt (dəqiqə)')
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Öyrənmə Tərəqqisi'
        verbose_name_plural = 'Öyrənmə Tərəqqiləri'
        unique_together = ['user', 'material']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.material.title} ({self.progress_percentage}%)"
