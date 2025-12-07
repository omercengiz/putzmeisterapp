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

    month = forms.ChoiceField(
        required=True,
        choices=[(m, calendar.month_name[m]) for m in range(1, 13)],
        label="Month"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'].label_from_instance = lambda obj: (obj.sicil_no or "").strip()

        for f in ['aile_yakacak', 'erzak', 'altin', 'bayram',
                  'dogum_evlenme', 'fon', 'harcirah', 'yol_parasi', 'prim']:
            self.fields[f].widget = forms.NumberInput(attrs={'step': '0.01', 'min': '0'})

    def clean(self):
        cleaned = super().clean()
        worker = cleaned.get('worker')
        year = cleaned.get('year')
        month = cleaned.get('month')

        if worker and year and month:
            exists = Benefit.objects.filter(worker=worker, year=year, month=month)\
                                    .exclude(pk=self.instance.pk).exists()
            if exists:
                msg = "Bu çalışan için bu ayda/yılda zaten bir kayıt var."
                self.add_error('worker', msg)
                self.add_error('month', msg)
        return cleaned

    class Meta:
        model = Benefit
        fields = [
            'worker', 'year', 'month',
            'aile_yakacak', 'erzak', 'altin', 'bayram',
            'dogum_evlenme', 'fon', 'harcirah', 'yol_parasi', 'prim'
        ]


# -------- Bulk monthly form --------

MONTH_CHOICES = [(m, calendar.month_name[m]) for m in range(1, 13)]  


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