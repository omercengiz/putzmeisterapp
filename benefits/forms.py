from django import forms
from django.core.validators import MinValueValidator
from .models import Benefit
from workers.models import Workers
import datetime

class BenefitForm(forms.ModelForm):
    worker = forms.ModelChoiceField(
        queryset=Workers.objects.all().order_by('sicil_no'),
        to_field_name='sicil_no',
        required=True,
        label='Sicil No (Worker)',
        help_text='Select the employee to assign the benefit.',
        empty_label="— Select Worker —",
    )

    period = forms.DateField(
        input_formats=['%Y-%m'],                                 # geleni böyle oku
        widget=forms.DateInput(format='%Y-%m', attrs={           # böyle render et
            'type': 'month',
            'placeholder': 'YYYY-MM',
            'pattern': r'\d{4}-\d{2}',
        }),
        label='Benefit Period',
        required=True,
        error_messages={'invalid': 'Geçerli bir ay seçin (YYYY-AA).'},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # UI'da sadece name_surname göster:
        self.fields['worker'].label_from_instance = lambda obj: (obj.sicil_no or "").strip()
        # (İstersen: self.fields['worker'].label_from_instance = lambda obj: f"P{obj.sicil_no} - {obj.name_surname}")

    def clean(self):
        cleaned = super().clean()
        worker = cleaned.get('worker')
        period = cleaned.get('period')

        if not worker or not period:
            return cleaned

        # Aynı çalışan + aynı ay için başka kayıt var mı? (kendi kaydını hariç tut)
        exists = Benefit.objects.filter(worker=worker, period=period)\
                                .exclude(pk=self.instance.pk).exists()
        if exists:
            msg = "Bu çalışan için bu ayda zaten bir kayıt var."
            # Alanların altına mesaj düş
            self.add_error('worker', msg)
            self.add_error('period', msg)
        return cleaned


    class Meta:
        model = Benefit
        fields = [
            'worker', 'period',
            'aile_yakacak', 'erzak', 'altin', 'bayram',
            'dogum_evlenme', 'fon', 'harcirah', 'yol_parasi', 'prim'
        ]
        widgets = {
            'period': forms.DateInput(attrs={'type': 'month'}),
            **{
                field: forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
                for field in [
                    'aile_yakacak', 'erzak', 'altin', 'bayram',
                    'dogum_evlenme', 'fon', 'harcirah', 'yol_parasi', 'prim'
                ]
            }
        }
