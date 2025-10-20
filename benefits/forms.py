# forms.py
import calendar
import datetime
from decimal import Decimal

from django import forms

from .models import Benefit
from workers.models import Workers


class BenefitForm(forms.ModelForm):
    worker = forms.ModelChoiceField(
        queryset=Workers.objects.all().order_by('sicil_no'),
        to_field_name='sicil_no',
        required=True,
        label='Sicil No (Worker)',
        help_text='Çalışanı seçin.',
        empty_label="— Select Worker —",
    )

    # YYYY-MM formatını kabul edip input’u <input type="month"> olarak render eder
    period = forms.DateField(
        input_formats=['%Y-%m'],
        widget=forms.DateInput(format='%Y-%m', attrs={'type': 'month', 'placeholder': 'YYYY-AA'}),
        label='Benefit Period',
        required=True,
        error_messages={'invalid': 'Geçerli bir ay seçin (YYYY-AA).'},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dropdown'da sadece sicil_no görünsün
        self.fields['worker'].label_from_instance = lambda obj: (obj.sicil_no or "").strip()
        # Sayısal alanların min/step ayarı
        for f in ['aile_yakacak', 'erzak', 'altin', 'bayram',
                  'dogum_evlenme', 'fon', 'harcirah', 'yol_parasi', 'prim']:
            self.fields[f].widget = forms.NumberInput(attrs={'step': '0.01', 'min': '0'})

    def clean_period(self):
        """
        type="month" ile gelen 'YYYY-MM' değeri DateField tarafından zaten
        1. gün olarak (YYYY-MM-01) parse edilir; yine de garanti altına alıyoruz.
        """
        val = self.cleaned_data.get('period')
        if isinstance(val, datetime.date):
            return val.replace(day=1)
        if isinstance(val, str) and len(val) == 7:
            return datetime.datetime.strptime(val, '%Y-%m').date().replace(day=1)
        return val

    def clean(self):
        cleaned = super().clean()
        worker = cleaned.get('worker')
        period = cleaned.get('period')
        if worker and period:
            exists = Benefit.objects.filter(worker=worker, period=period)\
                                    .exclude(pk=self.instance.pk).exists()
            if exists:
                msg = "Bu çalışan için bu ayda zaten bir kayıt var."
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


# -------- Bulk monthly form --------

MONTH_CHOICES = [(m, calendar.month_name[m]) for m in range(1, 13)]  # 1..12


class BenefitBulkForm(forms.Form):
    worker = forms.ModelChoiceField(
        queryset=Workers.objects.all().order_by('sicil_no'),
        to_field_name='sicil_no',
        required=True,
        label='Sicil No (Worker)',
        empty_label="— Select Worker —",
    )
    year = forms.IntegerField(
        required=True,
        min_value=2000,
        max_value=2100,
        initial=datetime.date.today().year,
        label="Year",
        widget=forms.NumberInput(attrs={'min': '2000', 'max': '2100'})
    )
    months = forms.MultipleChoiceField(
        required=True,
        choices=MONTH_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Months"
    )
    overwrite_existing = forms.BooleanField(
        required=False,
        initial=True,
        label="Aynı ay zaten varsa değerleri güncelle (overwrite)."
    )

    # Toplu uygulanan tutarlar
    aile_yakacak = forms.DecimalField(label="Family", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))
    erzak        = forms.DecimalField(label="Provision", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))
    altin        = forms.DecimalField(label="Gold", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))
    bayram       = forms.DecimalField(label="Holiday", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))
    dogum_evlenme= forms.DecimalField(label="Birth & Marriage", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))
    fon          = forms.DecimalField(label="Funding", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))
    harcirah     = forms.DecimalField(label="Subsistence", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))
    yol_parasi   = forms.DecimalField(label="Fare", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))
    prim         = forms.DecimalField(label="Premium", max_digits=12, decimal_places=2, min_value=Decimal('0'), initial=Decimal('0'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'].label_from_instance = lambda obj: (obj.sicil_no or "").strip()

    def clean_months(self):
        data = self.cleaned_data.get("months") or []
        if not data:
            raise forms.ValidationError("You must select at least one month.")
        try:
            return sorted({int(m) for m in data})
        except Exception:
            raise forms.ValidationError("Invalid month selection.")


class BenefitImportForm(forms.Form):
    file = forms.FileField(
        label="Excel File (.xlsx)",
        help_text="Please upload a file in .xlsx format."
    )