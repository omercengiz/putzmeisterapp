from django import forms
from .models import Workers, WorkerGrossMonthly, Currency
import datetime
import calendar
from decimal import Decimal


class WorkersForm(forms.ModelForm):
    class Meta:
        model = Workers
        fields = [
            "group", 
            "sicil_no", 
            "s_no", 
            "department_short_name", 
            "department", 
            "short_class", 
            "name_surname", 
            "date_of_recruitment",
            "work_class", 
            "location_name",
            "class_name",
            "gross_payment",
            "currency",
            "bonus",
            "total_work_hours",
            "update_date_user"
        ]
        widgets = {
            'date_of_recruitment': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}),
            'update_date_user': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(WorkersForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Please select a group"

        # Eğer instance.pk varsa add mode
        if self.instance and self.instance.pk:
            self.fields['update_date_user'].required = True
        else:
            # instance.pk yoksa update mode
            self.fields['update_date_user'].required = False


MONTH_CHOICES = [(m, calendar.month_name[m]) for m in range(1, 13)]


class GrossSalaryBulkForm(forms.Form):
    worker = forms.ModelChoiceField(
        queryset=Workers.objects.all().order_by('sicil_no'),
        to_field_name='sicil_no',
        required=True,
        label='Sicil No (Worker)',
        empty_label="— Select Worker —",
    )
    year = forms.IntegerField(
        required=True, min_value=2000, max_value=2100,
        initial=datetime.date.today().year, label="Year",
        widget=forms.NumberInput(attrs={'min': '2000', 'max': '2100'})
    )
    months = forms.MultipleChoiceField(
        required=True, choices=MONTH_CHOICES,
        widget=forms.CheckboxSelectMultiple, label="Months"
    )
    overwrite_existing = forms.BooleanField(
        required=False, initial=True,
        label="Aynı ay zaten varsa değerleri güncelle (overwrite)."
    )

    # Burada initial vermiyoruz ki "0" değerinden dolayı override engellenmesin
    gross_salary_hourly = forms.DecimalField(
        label="Gross Salary Hourly", max_digits=15, decimal_places=2, min_value=Decimal('0')
    )

    # Currency FK dropdown
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),
        required=False,
        empty_label="—",
        label="Currency"
    )

    def __init__(self, *args, **kwargs):
        """
        - refresh=1 (worker değişti) geldiğinde currency ve gross_salary_hourly'ı
          Workers tablosundan ZORLA doldur.
        - refresh yoksa ve gross_salary_hourly boş ise yine Workers'tan doldur.
        """
        super().__init__(*args, **kwargs)
        self.fields['worker'].label_from_instance = lambda obj: (obj.sicil_no or "").strip()

        if self.is_bound:
            data = self.data.copy()
            worker_key = data.get('worker')       # sicil_no (to_field_name)
            refresh    = data.get('refresh')      # '1' ise auto-submit

            if worker_key:
                w = Workers.objects.filter(sicil_no=worker_key).select_related('currency').first()
                if w:
                    # currency'i her durumda otomatik set et (FK id)
                    data['currency'] = w.currency_id or ''
                    # gross_salary_hourly kuralı:
                    #  - refresh=1 ise hard update/insert yap worker.gross_payment_hourly ile doldur
                    #  - değilse ve alanı boş bıraktıysa yine doldur
                    if refresh == '1' or not data.get('gross_salary_hourly'):
                        data['gross_salary_hourly'] = (w.gross_payment_hourly or '')
                    self.data = data
        else:
            # GET/initial senaryosu (opsiyonel)
            w = self.initial.get('worker') if isinstance(self.initial, dict) else None
            if isinstance(w, Workers):
                self.fields['currency'].initial = w.currency_id or None
                if w.gross_payment_hourly is not None:
                    self.fields['gross_salary_hourly'].initial = w.gross_payment_hourly


class WorkerGrossMonthlyForm(forms.ModelForm):
    class Meta:
        model = WorkerGrossMonthly
        fields = ["year", "month", "gross_salary_hourly", "currency"]
        widgets = {
            "year": forms.NumberInput(attrs={"min": 2000, "max": 2100}),
            "month": forms.NumberInput(attrs={"min": 1, "max": 12}),
            "gross_salary_hourly": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "gross_payment": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

class WorkerImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Excel Dosyası",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".xlsx",
            }
        )
    )
