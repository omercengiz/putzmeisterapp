from django.contrib import admin
from .models import Benefit

@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ["sicil_no", "name_surname", "job_start_date", "department", "gross_salary"]
    search_fields = ["sicil_no", "name_surname"]