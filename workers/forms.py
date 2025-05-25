from django import forms
from .models import Workers

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
            "class_name",
            "gross_payment"
        ]
        widgets = {
            'date_of_recruitment': forms.DateInput(attrs={'type': 'date'})
        }
