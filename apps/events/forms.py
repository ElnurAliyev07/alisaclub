from django import forms
from .models import Booking, EventReview
from apps.membership.models import Child


class BookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Yalnız istifadəçinin uşaqlarını göstər
            self.fields['child'].queryset = Child.objects.filter(parent__user=user)
            self.fields['child'].widget.attrs.update({'class': 'form-select'})
    
    class Meta:
        model = Booking
        fields = ['child', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Əlavə qeydlər (isteğe bağlı)'
            }),
        }


class EventReviewForm(forms.ModelForm):
    class Meta:
        model = EventReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tədbir haqqında rəyinizi yazın...'
            }),
        }


class EventFilterForm(forms.Form):
    CATEGORY_CHOICES = [('', 'Bütün kateqoriyalar')]
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    age_group = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Event, EventCategory
        
        # Dynamically set AGE_GROUP_CHOICES
        self.fields['age_group'].choices = [('', 'Bütün yaş qrupları')] + Event.AGE_GROUP_CHOICES
        
        # Dynamically set category choices
        categories = EventCategory.objects.all()
        self.fields['category'].choices = self.CATEGORY_CHOICES + [(cat.id, cat.name) for cat in categories]