from django import forms
from django.core.validators import MinValueValidator
from .models import Benefit
from workers.models import Workers

class BenefitForm(forms.ModelForm):
    worker = forms.ModelChoiceField(
        queryset=Workers.objects.all().order_by('sicil_no'),
        to_field_name='sicil_no',
        required=True,
        label='Sicil No (Worker)',
        help_text='Select the employee to assign the benefit.',
        empty_label="— Select Worker —",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # UI'da sadece name_surname göster:
        self.fields['worker'].label_from_instance = lambda obj: (obj.sicil_no or "").strip()
        # (İstersen: self.fields['worker'].label_from_instance = lambda obj: f"P{obj.sicil_no} - {obj.name_surname}")


    class Meta:
        model = Benefit
        fields = [
            'worker',
            'aile_yakacak', 'erzak', 'altin', 'bayram',
            'dogum_evlenme', 'fon', 'harcirah', 'yol_parasi', 'prim'
        ]
        widgets = {
            field: forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
            for field in [
                'aile_yakacak', 'erzak', 'altin', 'bayram',
                'dogum_evlenme', 'fon', 'harcirah', 'yol_parasi', 'prim'
            ]
        }
