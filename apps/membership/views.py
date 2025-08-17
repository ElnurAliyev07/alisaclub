from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from .forms import CustomUserCreationForm, MemberProfileForm, ChildForm, UserUpdateForm
from .models import MemberProfile, Child, Membership

class CustomLoginView(LoginView):
    template_name = 'membership/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('membership:profile')

class CustomLogoutView(LogoutView):
    template_name = 'membership/logout.html'
    next_page = reverse_lazy('membership:login')
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

def membership(request):
    """Üzvlük səhifəsi"""
    return render(request, 'membership/membership.html')

def register(request):
    """Qeydiyyat səhifəsi"""
    plan = request.GET.get('plan', 'basic')  # Get plan from query parameter
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = MemberProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user = user_form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                
                # Create membership with selected plan
                Membership.objects.create(
                    profile=profile,
                    membership_type=plan if plan in ['basic', 'premium', 'family'] else 'basic'
                )
                
                login(request, user)
                messages.success(request, 'Qeydiyyat uğurla tamamlandı! Xoş gəlmisiniz!')
                return redirect('membership:profile')
    else:
        user_form = CustomUserCreationForm()
        profile_form = MemberProfileForm()
    
    return render(request, 'membership/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'selected_plan': plan
    })

@login_required
def profile(request):
    """Profil səhifəsi"""
    try:
        member_profile = request.user.member_profile
    except MemberProfile.DoesNotExist:
        member_profile = MemberProfile.objects.create(
            user=request.user,
            phone='',
            address='',
            emergency_contact='',
            emergency_phone=''
        )
        Membership.objects.create(
            profile=member_profile,
            membership_type='basic'
        )
    
    children = member_profile.children.all()
    
    return render(request, 'membership/profile.html', {
        'member_profile': member_profile,
        'children': children
    })

@login_required
def edit_profile(request):
    """Profil redaktəsi"""
    member_profile = get_object_or_404(MemberProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = MemberProfileForm(request.POST, instance=member_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profil uğurla yeniləndi!')
            return redirect('membership:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = MemberProfileForm(instance=member_profile)
    
    return render(request, 'membership/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def add_child(request):
    """Uşaq əlavə etmə"""
    member_profile = get_object_or_404(MemberProfile, user=request.user)
    
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = member_profile
            child.save()
            messages.success(request, f'{child.name} uğurla əlavə edildi!')
            return redirect('membership:profile')
    else:
        form = ChildForm()
    
    return render(request, 'membership/add_child.html', {'form': form})

@login_required
def edit_child(request, pk):
    """Uşaq məlumatlarını redaktə etmə"""
    child = get_object_or_404(Child, pk=pk, parent__user=request.user)
    
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, f'{child.name} məlumatları yeniləndi!')
            return redirect('membership:profile')
    else:
        form = ChildForm(instance=child)
    
    return render(request, 'membership/edit_child.html', {
        'form': form,
        'child': child
    })

@login_required
def child_detail(request, pk):
    """Uşaq detalları"""
    child = get_object_or_404(Child, pk=pk, parent__user=request.user)
    
    return render(request, 'membership/child_detail.html', {
        'child': child
    })