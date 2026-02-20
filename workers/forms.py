from django import forms
from .models import Workers, WorkerGrossMonthly, Currency
import datetime
import calendar
from decimal import Decimal
from benefits.utils import parse_tr_decimal


class WorkersForm(forms.ModelForm):
    gross_payment = forms.CharField(
        required=False,
        localize=True,
        widget=forms.TextInput(attrs={
            "class": "form-control tr-money",
            "placeholder": "0",
            "inputmode": "decimal"
        })
    )
    class Meta:
        model = Workers
        localized_fields = ('gross_payment',),
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
        labels = {
            "group": "Group",
            "sicil_no": "Sicil No",
            "s_no": "Cost Center",
            "department_short_name": "Director",
            "department": "Department",
            "short_class": "Short Class",
            "name_surname": "Name Surname",
            "date_of_recruitment": "Date of Recruitment",
            "work_class": "Work Class",
            "location_name": "Location Name",
            "class_name": "Class Name",
            "gross_payment":  "Gross Payment (Monthly Total)",
            "currency": "Currency",
            "bonus": "Bonus",
            "total_work_hours": "Total Work Hours (Monthly)",
            "update_date_user": "Update Date (Optional, YYYY-MM-DD)"
        }
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

    def clean_gross_payment(self):
        gross_payment = self.cleaned_data.get("gross_payment")
        gross_payment = parse_tr_decimal(gross_payment)

        if gross_payment is None or gross_payment <= 0:
            raise forms.ValidationError(
                "Gross payment must be greater than 0."
            )

        return gross_payment


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
        label="If the month already exists, update it."
    )

    # Burada initial vermiyoruz ki "0" değerinden dolayı override engellenmesin
    gross_salary_hourly = forms.CharField(
        label="Gross Salary Hourly",
        localize=True,
        widget=forms.TextInput(attrs={
            "class": "tr-money",
            "placeholder": "0",
            "inputmode": "decimal",
        })
    )

    # Currency FK dropdown
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),
        required=False,
        empty_label="—",
        label="Currency"
    )

    def clean_gross_salary_hourly(self):
        return parse_tr_decimal(
            self.cleaned_data.get("gross_salary_hourly")
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
    gross_salary_hourly = forms.CharField(
        localize=True,
        widget=forms.TextInput(attrs={
            "class": "tr-money",
            "inputmode": "decimal",
        })
    )
    class Meta:
        model = WorkerGrossMonthly
        fields = [
            "year",
            "month",
            "gross_salary_hourly",
            "currency",
            "bonus",
            "group",
            "short_class",
            "class_name",
            "department",
            "work_class",
            "location_name",
            "department_short_name",
            "s_no",
        ]

        labels = {
            "year": "Year",
            "month": "Month",
            "gross_salary_hourly":  "Gross Salary Hourly",
            "currency": "Currency",
            "bonus": "Bonus",
            "group": "Group",
            "short_class": "Short Class",
            "class_name": "Class Name",
            "department": "Department",
            "work_class": "Work Class",
            "location_name": "Location",
            "department_short_name": "Director",
            "s_no": "Cost Center",
        }
        widgets = {
            "year": forms.NumberInput(attrs={"min": 2000, "max": 2100}),
            "month": forms.NumberInput(attrs={"min": 1, "max": 12}),
            "gross_salary_hourly": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "gross_payment": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }
    def clean_gross_salary_hourly(self):
        return parse_tr_decimal(
            self.cleaned_data.get("gross_salary_hourly")
        )

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
