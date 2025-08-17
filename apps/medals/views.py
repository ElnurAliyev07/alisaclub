from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Medal, MedalCategory, UserMedal, VirtualPassport, Achievement, UserAchievement, Leaderboard
from apps.membership.models import Child


def medal_list(request):
    """Medal siyahısı"""
    categories = MedalCategory.objects.all()
    medals = Medal.objects.filter(is_active=True)
    
    # Filtr
    category_id = request.GET.get('category')
    medal_type = request.GET.get('type')
    rarity = request.GET.get('rarity')
    
    if category_id:
        medals = medals.filter(category_id=category_id)
    if medal_type:
        medals = medals.filter(medal_type=medal_type)
    if rarity:
        medals = medals.filter(rarity=rarity)
    
    return render(request, 'medals/medal_list.html', {
        'categories': categories,
        'medals': medals,
        'selected_category': category_id,
        'selected_type': medal_type,
        'selected_rarity': rarity,
        'medal_types': Medal.MEDAL_TYPES,  # Pass medal types
        'rarity_levels': Medal.RARITY_LEVELS  # Pass rarity levels
    })

def medal_detail(request, pk):
    """Medal detalları"""
    medal = get_object_or_404(Medal, pk=pk, is_active=True)
    
    # Bu medalı qazanan uşaqlar
    winners = UserMedal.objects.filter(medal=medal).select_related('child')[:10]
    
    return render(request, 'medals/medal_detail.html', {
        'medal': medal,
        'winners': winners
    })


@login_required
def user_medals(request):
    """İstifadəçinin medalları"""
    try:
        member_profile = request.user.member_profile
        children = member_profile.children.all()
    except:
        messages.error(request, 'Medalları görmək üçün profil məlumatlarınızı tamamlayın.')
        return redirect('membership:profile')
    
    if not children.exists():
        messages.info(request, 'Medal sistemindən istifadə etmək üçün uşaq məlumatlarını əlavə edin.')
        return redirect('membership:add_child')
    
    # Seçilmiş uşaq
    child_id = request.GET.get('child')
    if child_id:
        selected_child = get_object_or_404(Child, pk=child_id, parent=member_profile)
    else:
        selected_child = children.first()
    
    # Virtual pasport
    passport, created = VirtualPassport.objects.get_or_create(child=selected_child)
    
    # Medallar
    user_medals = UserMedal.objects.filter(child=selected_child).select_related('medal', 'medal__category')
    
    # Kateqoriya üzrə qruplaşdırma
    medals_by_category = {}
    for user_medal in user_medals:
        category = user_medal.medal.category.name
        if category not in medals_by_category:
            medals_by_category[category] = []
        medals_by_category[category].append(user_medal)
    
    # Nailiyyətlər
    achievements = UserAchievement.objects.filter(child=selected_child).select_related('achievement')
    
    # Statistikalar
    stats = {
        'total_medals': user_medals.count(),
        'bronze_medals': passport.bronze_medals,
        'silver_medals': passport.silver_medals,
        'gold_medals': passport.gold_medals,
        'total_points': passport.total_points,
        'level': passport.level,
        'achievements_count': achievements.count()
    }
    
    return render(request, 'medals/user_medals.html', {
        'children': children,
        'selected_child': selected_child,
        'passport': passport,
        'medals_by_category': medals_by_category,
        'achievements': achievements,
        'stats': stats
    })


@login_required
def virtual_passport(request, child_id):
    """Virtual pasport"""
    try:
        member_profile = request.user.member_profile
        child = get_object_or_404(Child, pk=child_id, parent=member_profile)
    except:
        messages.error(request, 'Pasportu görmək üçün profil məlumatlarınızı tamamlayın.')
        return redirect('membership:profile')
    
    passport, created = VirtualPassport.objects.get_or_create(child=child)
    
    # Son medallar
    recent_medals = UserMedal.objects.filter(child=child).select_related('medal')[:5]
    
    # Son nailiyyətlər
    recent_achievements = UserAchievement.objects.filter(child=child).select_related('achievement')[:5]
    
    # Xal tarixçəsi
    point_history = passport.point_history.all()[:10]
    
    return render(request, 'medals/virtual_passport.html', {
        'child': child,
        'passport': passport,
        'recent_medals': recent_medals,
        'recent_achievements': recent_achievements,
        'point_history': point_history
    })


def leaderboard(request):
    """Liderlik cədvəli"""
    period = request.GET.get('period', 'monthly')
    
    # Dövr hesabla
    today = timezone.now().date()
    if period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'monthly':
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    elif period == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:  # all_time
        start_date = None
        end_date = None
    
    # Liderlik cədvəli
    if period == 'all_time':
        leaders = VirtualPassport.objects.select_related('child').order_by('-total_points')[:20]
    else:
        leaders = Leaderboard.objects.filter(
            period=period,
            period_start=start_date
        ).select_related('child').order_by('rank')[:20]
    
    return render(request, 'medals/leaderboard.html', {
        'leaders': leaders,
        'period': period,
        'start_date': start_date,
        'end_date': end_date
    })


def achievements_list(request):
    """Nailiyyətlər siyahısı"""
    achievements = Achievement.objects.filter(is_active=True)
    
    # Növ üzrə filtr
    achievement_type = request.GET.get('type')
    if achievement_type:
        achievements = achievements.filter(achievement_type=achievement_type)
    
    return render(request, 'medals/achievements_list.html', {
        'achievements': achievements,
        'selected_type': achievement_type
    })


@login_required
def check_medal_eligibility(request):
    """Medal əldə etmə yoxlaması"""
    try:
        member_profile = request.user.member_profile
        children = member_profile.children.all()
    except:
        return redirect('membership:profile')
    
    new_medals = []
    
    for child in children:
        # Virtual pasport yarat
        passport, created = VirtualPassport.objects.get_or_create(child=child)
        
        # Mövcud medalları al
        existing_medals = set(UserMedal.objects.filter(child=child).values_list('medal_id', flat=True))
        
        # Bütün medalları yoxla
        for medal in Medal.objects.filter(is_active=True):
            if medal.id in existing_medals:
                continue
            
            # Şərtləri yoxla
            eligible = True
            
            # Tədbir sayı
            if medal.required_events > 0:
                event_count = child.bookings.filter(status='confirmed', attended=True).count()
                if event_count < medal.required_events:
                    eligible = False
            
            # Material sayı
            if medal.required_materials > 0:
                from apps.kids_content.models import LearningProgress
                completed_materials = LearningProgress.objects.filter(
                    user=child.parent.user,
                    status='completed'
                ).count()
                if completed_materials < medal.required_materials:
                    eligible = False
            
            # Xal
            if medal.required_points > 0:
                if passport.total_points < medal.required_points:
                    eligible = False
            
            # Tələb olunan medallər
            if medal.required_medals.exists():
                required_medal_ids = set(medal.required_medals.values_list('id', flat=True))
                if not required_medal_ids.issubset(existing_medals):
                    eligible = False
            
            # Medal ver
            if eligible:
                user_medal = UserMedal.objects.create(
                    user=request.user,
                    child=child,
                    medal=medal
                )
                
                # Xal əlavə et
                passport.add_points(medal.points, f"Medal: {medal.name}")
                
                new_medals.append(user_medal)
    
    if new_medals:
        messages.success(request, f'{len(new_medals)} yeni medal qazandınız!')
    
    return redirect('medals:user_medals')
