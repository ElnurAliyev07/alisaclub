
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BirthdayPackage, BirthdayBooking, BirthdayInquiry
from .forms import BirthdayBookingForm, BirthdayInquiryForm

def package_list(request):
    packages = BirthdayPackage.objects.filter(is_active=True).order_by('price')
    
    context = {
        'packages': packages,
        'page_title': 'Ad Günü Paketləri'
    }
    return render(request, 'birthday/package_list.html', context)

def package_detail(request, pk):
    package = get_object_or_404(BirthdayPackage, pk=pk, is_active=True)
    
    context = {
        'package': package,
        'page_title': package.name
    }
    return render(request, 'birthday/package_detail.html', context)

@login_required
def book_birthday(request, package_id):
    package = get_object_or_404(BirthdayPackage, pk=package_id, is_active=True)
    
    if request.method == 'POST':
        form = BirthdayBookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.parent = request.user
            booking.total_price = package.price
            booking.save()
            
            messages.success(request, 'Ad günü rezervasiyası uğurla yaradıldı! Tezliklə sizinlə əlaqə saxlayacağıq.')
            return redirect('birthday:my_bookings')
    else:
        form = BirthdayBookingForm(user=request.user, initial={'package': package})
    
    context = {
        'form': form,
        'package': package,
        'page_title': f'{package.name} - Rezervasiya'
    }
    return render(request, 'birthday/book_birthday.html', context)

@login_required
def my_bookings(request):
    bookings = BirthdayBooking.objects.filter(parent=request.user).order_by('-booking_date')
    
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': 'Mənim Rezervasiyalarım'
    }
    return render(request, 'birthday/my_bookings.html', context)

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(BirthdayBooking, pk=pk, parent=request.user)
    
    context = {
        'booking': booking,
        'page_title': f'Rezervasiya #{booking.id}'
    }
    return render(request, 'birthday/booking_detail.html', context)


def planner(request):
    if request.method == 'POST':
        form = BirthdayInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            if request.user.is_authenticated:
                inquiry.parent = request.user
            inquiry.save()
            messages.success(request, 'Doğum günü sorğunuz qeydə alındı! Tezliklə sizinlə əlaqə saxlayacağıq.')
            return redirect('home')
    else:
        form = BirthdayInquiryForm()
    
    context = {
        'form': form,
        'page_title': 'Doğum Günü Planlayıcısı'
    }
    return render(request, 'birthday/planner.html', context)
