from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
from .models import Event, EventCategory, Booking, EventReview
from .forms import BookingForm, EventReviewForm, EventFilterForm


def event_list(request):
    """Tədbir siyahısı"""
    events = Event.objects.filter(status='upcoming', date__gte=timezone.now())
    categories = EventCategory.objects.all()
    
    # Filtrlər
    form = EventFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['category']:
            events = events.filter(category_id=form.cleaned_data['category'])
        if form.cleaned_data['age_group']:
            events = events.filter(age_group=form.cleaned_data['age_group'])
        if form.cleaned_data['date_from']:
            events = events.filter(date__date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data['date_to']:
            events = events.filter(date__date__lte=form.cleaned_data['date_to'])
    
    # Axtarış
    search = request.GET.get('search')
    if search:
        events = events.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Səhifələmə
    paginator = Paginator(events, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'events/event_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'form': form,
        'search': search
    })

def event_list_preview(request):
    """Ən son 3 gələcək tədbiri göstərən önizləmə"""
    events = Event.objects.filter(status='upcoming', date__gte=timezone.now())[:3]
    return render(request, 'events/event_list_preview.html', {
        'events': events
    })

def event_detail(request, pk):
    """Tədbir detalları"""
    event = get_object_or_404(Event, pk=pk)
    reviews = event.reviews.all()[:5]
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    user_booking = None
    user_review = None
    can_review = False
    
    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(
            event=event, 
            user=request.user
        ).first()
        
        user_review = EventReview.objects.filter(
            event=event,
            user=request.user
        ).first()
        
        # Rəy yaza bilər əgər tədbirə qatılıbsa və hələ rəy yazmaıbsa
        can_review = (user_booking and 
                     user_booking.attended and 
                     not user_review and
                     event.date < timezone.now())
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_booking': user_booking,
        'user_review': user_review,
        'can_review': can_review
    })

@login_required
def book_event(request, pk):
    """Tədbir rezervasiyası"""
    event = get_object_or_404(Event, pk=pk)
    
    # Yoxlamalar
    if event.is_full:
        messages.error(request, 'Bu tədbir üçün yer qalmayıb.')
        return redirect('events:event_detail', pk=pk)
    
    if event.date < timezone.now():
        messages.error(request, 'Bu tədbir artıq keçmişdə qalıb.')
        return redirect('events:event_detail', pk=pk)
    
    # İstifadəçinin uşaqları var mı?
    try:
        member_profile = request.user.member_profile
        if not member_profile.children.exists():
            messages.error(request, 'Rezervasiya etmək üçün əvvəlcə uşaq məlumatlarını əlavə edin.')
            return redirect('membership:add_child')
    except:
        messages.error(request, 'Rezervasiya etmək üçün əvvəlcə profil məlumatlarınızı tamamlayın.')
        return redirect('membership:profile')
    
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            # Eyni uşaq üçün rezervasiya var mı?
            existing_booking = Booking.objects.filter(
                event=event,
                child=form.cleaned_data['child']
            ).first()
            
            if existing_booking:
                messages.error(request, 'Bu uşaq üçün artıq rezervasiya mövcuddur.')
            else:
                booking = form.save(commit=False)
                booking.event = event
                booking.user = request.user
                booking.status = 'confirmed'
                booking.save()
                
                messages.success(request, 'Rezervasiya uğurla tamamlandı!')
                return redirect('events:booking_success', booking_id=booking.id)
    else:
        form = BookingForm(user=request.user)
    
    return render(request, 'events/book_event.html', {
        'event': event,
        'form': form
    })

@login_required
def booking_success(request, booking_id):
    """Rezervasiya uğur səhifəsi"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'events/booking_success.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    """Rezervasiyanı ləğv et"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if not booking.can_cancel:
        messages.error(request, 'Bu rezervasiyanı ləğv etmək mümkün deyil.')
        return redirect('membership:profile')
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Rezervasiya ləğv edildi.')
        return redirect('membership:profile')
    
    return render(request, 'events/cancel_booking.html', {'booking': booking})

@login_required
def add_review(request, pk):
    """Tədbir rəyi əlavə et"""
    event = get_object_or_404(Event, pk=pk)
    
    # İstifadəçi bu tədbirə qatılıb mı?
    booking = Booking.objects.filter(
        event=event,
        user=request.user,
        attended=True
    ).first()
    
    if not booking:
        messages.error(request, 'Yalnız qatıldığınız tədbirlər üçün rəy yaza bilərsiniz.')
        return redirect('events:event_detail', pk=pk)
    
    # Artıq rəy yazıb mı?
    if EventReview.objects.filter(event=event, user=request.user).exists():
        messages.error(request, 'Bu tədbir üçün artıq rəy yazmısınız.')
        return redirect('events:event_detail', pk=pk)
    
    if request.method == 'POST':
        form = EventReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.event = event
            review.user = request.user
            review.save()
            messages.success(request, 'Rəyiniz əlavə edildi!')
            return redirect('events:event_detail', pk=pk)
    else:
        form = EventReviewForm()
    
    return render(request, 'events/add_review.html', {
        'event': event,
        'form': form
    })

@login_required
def my_bookings(request):
    """İstifadəçinin rezervasiyaları"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    return render(request, 'events/my_bookings.html', {
        'bookings': bookings
    })