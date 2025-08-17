from django import forms
from .models import Subscription, ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adınız'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email ünvanınız'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Mesajınız'
            })
        }

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control subscribe-input-modern',
                'placeholder': 'E-poçt ünvanınızı daxil edin',
                'required': True
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('E-poçt ünvanı boş ola bilməz.')
        if Subscription.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError('Bu e-poçt ünvanı artıq abunədir. Başqa e-poçt sınayın.')
        return email