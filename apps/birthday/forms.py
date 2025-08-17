from django import forms
from .models import BirthdayBooking, BirthdayPackage, BirthdayInquiry
from apps.membership.models import Child
from datetime import timezone

class BirthdayBookingForm(forms.ModelForm):
    class Meta:
        model = BirthdayBooking
        fields = ['child', 'package', 'booking_date', 'guest_count', 'special_requests', 'contact_phone']
        widgets = {
            'child': forms.Select(attrs={'class': 'form-select'}),
            'package': forms.Select(attrs={'class': 'form-select'}),
            'booking_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'guest_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['child'].queryset = Child.objects.filter(parent=user)
        
        self.fields['package'].queryset = BirthdayPackage.objects.filter(is_active=True)
    
    def clean_guest_count(self):
        guest_count = self.cleaned_data.get('guest_count')
        package = self.cleaned_data.get('package')
        
        if package and guest_count > package.max_guests:
            raise forms.ValidationError(f'Bu paket maksimum {package.max_guests} qonaq üçün nəzərdə tutulub.')
        
        return guest_count


class BirthdayInquiryForm(forms.ModelForm):
    class Meta:
        model = BirthdayInquiry
        fields = ['child_name', 'child_age', 'event_date', 'guest_count', 'theme', 'notes', 'contact_phone']
        widgets = {
            'child_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Uşağın adını daxil edin'}),
            'child_age': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '18'}),
            'event_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'guest_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'theme': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Xüsusi istəklərinizi buraya yazın'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Əlaqə telefonu'}),
        }
    
    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        if event_date < timezone.now().date():
            raise forms.ValidationError('Doğum günü tarixi gələcəkdə olmalıdır.')
        return event_date