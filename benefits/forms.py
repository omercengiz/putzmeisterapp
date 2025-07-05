from django import forms
from .models import Benefit

class BenefitForm(forms.ModelForm):
    class Meta:
        model = Benefit
        fields = '__all__'
        widgets = {
            'kidem_tarihi': forms.DateInput(attrs={'type': 'date'})
        }
