# benefits/admin.py
from django.contrib import admin
from .models import Benefit

@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = (
        'worker', 'name_surname', 'cost_center_id', 'group_name',
        'yurtici_harcirah', 'yurtdisi_harcirah', 'yol_yardimi',
        'yemek_ticket', 'dogum_yardimi', 'evlenme_yardimi'
    )
    search_fields = ('worker__sicil_no', 'worker__name_surname')
