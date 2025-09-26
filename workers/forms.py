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
            "gross_payment",
            "currency",
            "bonus"
        ]
        widgets = {
            'date_of_recruitment': forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(WorkersForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Please select a group"
