from django import forms
from .models import MaterialRating, KidsMaterial


class MaterialRatingForm(forms.ModelForm):
    class Meta:
        model = MaterialRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Material haqqında rəyinizi yazın...'
            }),
        }


class MaterialFilterForm(forms.Form):
    CATEGORY_CHOICES = [('', 'Bütün kateqoriyalar')]
    TYPE_CHOICES = [('', 'Bütün növlər')] + KidsMaterial.MATERIAL_TYPES
    AGE_GROUP_CHOICES = [('', 'Bütün yaş qrupları')] + KidsMaterial.AGE_GROUPS
    DIFFICULTY_CHOICES = [('', 'Bütün səviyyələr')] + KidsMaterial.DIFFICULTY_LEVELS
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    material_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    age_group = forms.ChoiceField(
        choices=AGE_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    difficulty_level = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_premium = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ContentCategory
        categories = ContentCategory.objects.all()
        self.fields['category'].choices += [(cat.id, cat.name) for cat in categories]
