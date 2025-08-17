from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import HttpResponse, Http404
from django.utils import timezone
from .models import KidsMaterial, ContentCategory, MaterialRating, Favorite, LearningProgress, MaterialDownload
from .forms import MaterialRatingForm, MaterialFilterForm


def material_list(request):
    """Material siyahısı"""
    materials = KidsMaterial.objects.all()
    categories = ContentCategory.objects.all()
    
    # Filtrlər
    form = MaterialFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['category']:
            materials = materials.filter(category_id=form.cleaned_data['category'])
        if form.cleaned_data['material_type']:
            materials = materials.filter(material_type=form.cleaned_data['material_type'])
        if form.cleaned_data['age_group']:
            materials = materials.filter(age_group=form.cleaned_data['age_group'])
        if form.cleaned_data['difficulty_level']:
            materials = materials.filter(difficulty_level=form.cleaned_data['difficulty_level'])
        if form.cleaned_data['is_premium']:
            materials = materials.filter(is_premium=True)
    
    # Axtarış
    search = request.GET.get('search')
    if search:
        materials = materials.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(content__icontains=search)
        )
    
    # Sıralama
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'popular':
        materials = materials.order_by('-view_count', '-download_count')
    elif sort_by == 'rating':
        materials = materials.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')
    else:
        materials = materials.order_by(sort_by)
    
    # Seçilmiş materiallar
    featured_materials = KidsMaterial.objects.filter(is_featured=True)[:6]
    
    # Səhifələmə
    paginator = Paginator(materials, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'kids_content/material_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'featured_materials': featured_materials,
        'form': form,
        'search': search,
        'sort_by': sort_by
    })


def material_detail(request, pk):
    """Material detalları"""
    material = get_object_or_404(KidsMaterial, pk=pk)
    
    # Baxış sayını artır
    material.increment_view_count()
    
    # Rəylər
    ratings = material.ratings.all()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    
    # İstifadəçi məlumatları
    user_rating = None
    is_favorite = False
    user_progress = None
    
    if request.user.is_authenticated:
        user_rating = MaterialRating.objects.filter(
            material=material,
            user=request.user
        ).first()
        
        is_favorite = Favorite.objects.filter(
            material=material,
            user=request.user
        ).exists()
        
        user_progress, created = LearningProgress.objects.get_or_create(
            material=material,
            user=request.user
        )
    
    # Oxşar materiallar
    related_materials = KidsMaterial.objects.filter(
        category=material.category,
        age_group=material.age_group
    ).exclude(pk=material.pk)[:4]
    
    return render(request, 'kids_content/material_detail.html', {
        'material': material,
        'ratings': ratings[:5],
        'avg_rating': avg_rating,
        'user_rating': user_rating,
        'is_favorite': is_favorite,
        'user_progress': user_progress,
        'related_materials': related_materials
    })


@login_required
def download_material(request, pk):
    """Material yükləmə"""
    material = get_object_or_404(KidsMaterial, pk=pk)
    
    if not material.file:
        messages.error(request, 'Bu material üçün fayl mövcud deyil.')
        return redirect('kids_content:material_detail', pk=pk)
    
    # Premium yoxlaması
    if material.is_premium:
        try:
            membership = request.user.member_profile.membership
            if membership.membership_type == 'basic':
                messages.error(request, 'Bu premium məzmun üçün üzvlüyünüzü yeniləyin.')
                return redirect('kids_content:material_detail', pk=pk)
        except:
            messages.error(request, 'Premium məzmun üçün üzvlük tələb olunur.')
            return redirect('kids_content:material_detail', pk=pk)
    
    # Yükləmə qeydini yarat
    MaterialDownload.objects.create(
        material=material,
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # Yükləmə sayını artır
    material.increment_download_count()
    
    # Faylı göndər
    response = HttpResponse(material.file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{material.file.name}"'
    return response


@login_required
def add_rating(request, pk):
    """Material qiyməti əlavə et"""
    material = get_object_or_404(KidsMaterial, pk=pk)
    
    # Artıq qiymət verib mi?
    if MaterialRating.objects.filter(material=material, user=request.user).exists():
        messages.error(request, 'Bu material üçün artıq qiymət vermişsiniz.')
        return redirect('kids_content:material_detail', pk=pk)
    
    if request.method == 'POST':
        form = MaterialRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.material = material
            rating.user = request.user
            rating.save()
            messages.success(request, 'Qiymətiniz əlavə edildi!')
            return redirect('kids_content:material_detail', pk=pk)
    else:
        form = MaterialRatingForm()
    
    return render(request, 'kids_content/add_rating.html', {
        'material': material,
        'form': form
    })


@login_required
def toggle_favorite(request, pk):
    """Sevimli əlavə et/sil"""
    material = get_object_or_404(KidsMaterial, pk=pk)
    
    favorite, created = Favorite.objects.get_or_create(
        material=material,
        user=request.user
    )
    
    if not created:
        favorite.delete()
        messages.success(request, 'Sevimlilərdən silindi.')
    else:
        messages.success(request, 'Sevimlilərə əlavə edildi.')
    
    return redirect('kids_content:material_detail', pk=pk)


@login_required
def my_favorites(request):
    """İstifadəçinin sevimli materialları"""
    favorites = Favorite.objects.filter(user=request.user).select_related('material')
    
    return render(request, 'kids_content/my_favorites.html', {
        'favorites': favorites
    })


@login_required
def my_progress(request):
    """İstifadəçinin öyrənmə tərəqqisi"""
    progress_records = LearningProgress.objects.filter(
        user=request.user
    ).select_related('material').order_by('-last_accessed')
    
    return render(request, 'kids_content/my_progress.html', {
        'progress_records': progress_records
    })


@login_required
def update_progress(request, pk):
    """Tərəqqi yenilə"""
    material = get_object_or_404(KidsMaterial, pk=pk)
    
    progress, created = LearningProgress.objects.get_or_create(
        material=material,
        user=request.user
    )
    
    if request.method == 'POST':
        status = request.POST.get('status')
        progress_percentage = int(request.POST.get('progress_percentage', 0))
        
        progress.status = status
        progress.progress_percentage = progress_percentage
        
        if status == 'completed' and not progress.completed_at:
            progress.completed_at = timezone.now()
        
        progress.save()
        messages.success(request, 'Tərəqqi yeniləndi!')
    
    return redirect('kids_content:material_detail', pk=pk)


def category_materials(request, category_id):
    """Kateqoriya materialları"""
    category = get_object_or_404(ContentCategory, pk=category_id)
    materials = category.materials.all().order_by('-created_at')
    
    # Səhifələmə
    paginator = Paginator(materials, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'kids_content/category_materials.html', {
        'category': category,
        'page_obj': page_obj
    })
