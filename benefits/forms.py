from django import forms
from django.core.validators import MinValueValidator
from .models import Benefit
from workers.models import Workers

class BenefitForm(forms.ModelForm):
    # Worker choice (OneToOne)
    worker = forms.ModelChoiceField(
        queryset=Workers.objects.all().order_by('sicil_no'),
        to_field_name='sicil_no',
        required=True,
        label='Sicil No (Worker)',
        help_text='Yan hak tanımlanacak çalışanı seçin (sicil no).'
    )

    class Meta:
        model = Benefit
        fields = [
            'worker',
            'yurtici_harcirah', 'yurtdisi_harcirah',
            'yol_yardimi', 'yemek_ticket',
            'dogum_yardimi', 'evlenme_yardimi'
        ]
        widgets = {
            'yurtici_harcirah':  forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'yurtdisi_harcirah': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'yol_yardimi':       forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'yemek_ticket':      forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'dogum_yardimi':     forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'evlenme_yardimi':   forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
