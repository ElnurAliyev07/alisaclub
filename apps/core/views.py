from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from apps.events.models import Event
from apps.blog.models import BlogPost  # Assuming you have a BlogPost model for latest_posts
from .forms import ContactForm, SubscriptionForm
from django.utils import timezone

def home(request):
    """Ana səhifə"""
    events = Event.objects.filter(status='upcoming', date__gte=timezone.now())[:3]
    latest_posts = BlogPost.objects.order_by('-created_at')[:3]
    context = {
        'subscribe_form': SubscriptionForm(),
        'events': events,
        'latest_posts': latest_posts,
    }
    
    return render(request, 'core/home.html', context)

def contact(request):
    """Əlaqə səhifəsi"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            # Email göndərişi
            try:
                send_mail(
                    f'Alisa Club - {contact_message.name} tərəfindən mesaj',
                    f'Ad: {contact_message.name}\nEmail: {contact_message.email}\n\nMesaj:\n{contact_message.message}',
                    settings.EMAIL_HOST_USER,
                    ['info@alisaclub.az'],
                    fail_silently=False,
                )
                messages.success(request, 'Mesajınız uğurla göndərildi!')
                return redirect('core:contact')
            except Exception as e:
                messages.error(request, 'Mesaj göndərilmədi. Xahiş edirik yenidən cəhd edin.')
        else:
            messages.error(request, 'Mesaj göndərilmədi. Formada xəta var.')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})

def about(request):
    """Haqqımızda səhifəsi"""
    return render(request, 'core/about.html')

def subscribe(request):
    """Abunəlik səhifəsi"""
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            if request.user.is_authenticated:
                subscription.user = request.user
            subscription.save()
            # Təsdiq e-poçtu (istəyə bağlı)
            try:
                send_mail(
                    'Alisa Club Abunəliyi',
                    'Xəbərlərimizə abunə olduğunuz üçün təşəkkür edirik!',
                    settings.EMAIL_HOST_USER,
                    [subscription.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # E-poçt göndərilməsə belə abunəlik saxlanılır
            messages.success(request, 'Abunəliyiniz uğurla qeydə alındı! Xəbərlərimizi gözləyin!')
            return redirect('core:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            context = {
                'subscribe_form': form,
            }
            return render(request, 'core/home.html', context)
    return redirect('core:home')