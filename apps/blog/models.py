from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Kateqoriya Adı')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Təsvir')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Rəng')
    icon = models.CharField(max_length=50, default='fas fa-folder', verbose_name='İkon')
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Blog Kateqoriyası'
        verbose_name_plural = 'Blog Kateqoriyaları'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qaralama'),
        ('published', 'Dərc Edildi'),
        ('archived', 'Arxivləndi'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Başlıq')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Müəllif')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, verbose_name='Kateqoriya')
    excerpt = models.TextField(max_length=300, verbose_name='Qısa Məzmun')
    content = models.TextField(verbose_name='Məzmun')
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, verbose_name='Əsas Şəkil')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Status')
    is_featured = models.BooleanField(default=False, verbose_name='Seçilmiş')
    tags = models.CharField(max_length=200, blank=True, verbose_name='Etiketlər')
    read_time = models.IntegerField(default=5, verbose_name='Oxuma Müddəti (dəqiqə)')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Baxış Sayı')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='Dərc Tarixi')
    
    class Meta:
        verbose_name = 'Blog Yazısı'
        verbose_name_plural = 'Blog Yazıları'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments', verbose_name='Yazı')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Müəllif')
    content = models.TextField(verbose_name='Şərh')
    is_approved = models.BooleanField(default=False, verbose_name='Təsdiqləndi')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Blog Şərhi'
        verbose_name_plural = 'Blog Şərhləri'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.author.username} - {self.post.title}'


