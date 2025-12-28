# forms.py
import calendar
import datetime
from decimal import Decimal

from django import forms

from .models import Benefit
from workers.models import Workers


# =====================================================
# SINGLE BENEFIT FORM
# =====================================================

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
        self.fields['worker'].label_from_instance = (
            lambda obj: (obj.sicil_no or "").strip()
        )

        for f in [
            'aile_yakacak', 'erzak', 'altin', 'bayram',
            'dogum_evlenme', 'fon', 'harcirah',
            'yol_parasi', 'prim'
        ]:
            self.fields[f].widget = forms.NumberInput(
                attrs={'step': '0.01', 'min': '0'}
            )

    def clean(self):
        cleaned = super().clean()
        worker = cleaned.get('worker')
        year = cleaned.get('year')
        month = cleaned.get('month')

        if worker and year and month:
            exists = (
                Benefit.objects
                .filter(worker=worker, year=year, month=month)
                .exclude(pk=self.instance.pk)
                .exists()
            )
            if exists:
                msg = "Bu çalışan için bu ay/yılda zaten bir kayıt var."
                self.add_error('worker', msg)
                self.add_error('month', msg)

        return cleaned

    class Meta:
        model = Benefit
        fields = [
            'worker', 'year', 'month',
            'aile_yakacak', 'erzak', 'altin', 'bayram',
            'dogum_evlenme', 'fon', 'harcirah',
            'yol_parasi', 'prim'
        ]


# =====================================================
# BULK BENEFIT FORM (SHORT CLASS AWARE)
# =====================================================

MONTH_CHOICES = [(m, calendar.month_name[m]) for m in range(1, 13)]


class BenefitBulkForm(forms.Form):
    worker = forms.ModelChoiceField(
        queryset=Workers.objects.all().order_by('sicil_no'),
        to_field_name='sicil_no',
        required=False,   # 🔥 KRİTİK
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
        label="Aynı ay zaten varsa overwrite et"
    )

    # Values
    aile_yakacak  = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)
    erzak         = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)
    altin         = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)
    bayram        = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)
    dogum_evlenme = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)
    fon           = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)
    harcirah      = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)
    yol_parasi    = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)
    prim          = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0, initial=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'].label_from_instance = (
            lambda obj: (obj.sicil_no or "").strip()
        )

    def clean_months(self):
        months = self.cleaned_data.get("months") or []
        if not months:
            raise forms.ValidationError("En az bir ay seçmelisiniz.")
        return sorted({int(m) for m in months})

    def clean(self):
        """
        🔥 ASIL MANTIK BURADA
        """
        cleaned = super().clean()

        worker = cleaned.get("worker")
        short_class = self.data.get("short_class_action")

        # ❌ Short class YOK → worker zorunlu
        if not short_class and not worker:
            self.add_error(
                "worker",
                "Sicil No zorunludur (Short Class seçilmediyse)."
            )

        return cleaned


# =====================================================
# IMPORT FORM
# =====================================================

class BenefitImportForm(forms.Form):
    file = forms.FileField(
        label="Excel File (.xlsx)",
        help_text="Please upload a file in .xlsx format."
    )
