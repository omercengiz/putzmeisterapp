# forms.py
import calendar
import datetime
from decimal import Decimal

from django import forms

from .models import Benefit
from workers.models import Workers
from .utils import parse_tr_decimal




def money_field():
    return forms.CharField(
        required=False,
        initial="0",
        widget=forms.TextInput(attrs={
            "class": "tr-money",
            "placeholder": "0",
            "inputmode": "decimal",
        })
    )

class SicilNoChoiceField(forms.ModelChoiceField):
    """Dropdown ve search'te sadece sicil_no göster"""
    def label_from_instance(self, obj):
        return str(obj.sicil_no)


class BenefitForm(forms.ModelForm):
    worker = SicilNoChoiceField(
        queryset=Workers.objects.only("id", "sicil_no").order_by("sicil_no"),
        required=True,
        label="Sicil No (Worker)",
        empty_label="— Select Worker —",
    )

    year = forms.IntegerField(
        label="Year",
        min_value=2000,
        max_value=2100,
        initial=datetime.date.today().year,
        widget=forms.NumberInput(attrs={"min": 2000, "max": 2100}),
    )

    month = forms.ChoiceField(
        label="Month",
        choices=[(m, calendar.month_name[m]) for m in range(1, 13)],
    )

    # 🔥 Money fields (label override)
    aile_yakacak  = money_field()
    erzak         = money_field()
    altin         = money_field()
    bayram        = money_field()
    dogum_evlenme = money_field()
    fon           = money_field()
    harcirah      = money_field()
    yol_parasi    = money_field()
    prim          = money_field()

    class Meta:
        model = Benefit
        fields = [
            "worker", "year", "month",
            "aile_yakacak", "erzak", "altin", "bayram",
            "dogum_evlenme", "fon", "harcirah",
            "yol_parasi", "prim",
        ]

    def clean(self):
        cleaned = super().clean()

        worker = cleaned.get("worker")
        year   = cleaned.get("year")
        month  = cleaned.get("month")

        # Uniqueness check
        if worker and year and month:
            exists = Benefit.objects.filter(
                worker=worker, year=year, month=month
            ).exclude(pk=self.instance.pk).exists()
            if exists:
                msg = "This worker already has a record for this year/month."
                self.add_error("worker", msg)
                self.add_error("month", msg)

        # TR format → Decimal
        for f in [
            "aile_yakacak", "erzak", "altin", "bayram",
            "dogum_evlenme", "fon", "harcirah",
            "yol_parasi", "prim",
        ]:
            cleaned[f] = parse_tr_decimal(cleaned.get(f))

        return cleaned



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
        label="If the month already exists, update it."
    )

    # Values
    aile_yakacak = money_field()
    erzak        = money_field()
    altin        = money_field()
    bayram       = money_field()
    dogum_evlenme= money_field()
    fon          = money_field()
    harcirah     = money_field()
    yol_parasi   = money_field()
    prim         = money_field()

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
