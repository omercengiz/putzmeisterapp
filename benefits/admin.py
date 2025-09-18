from django.contrib import admin
from .models import Benefit

@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = (
        'worker', 'name_surname', 'cost_center_id', 'group_name',
        'aile_yakacak','erzak','altin','bayram',
        'dogum_evlenme','fon','harcirah','yol_parasi','prim'
    )
    search_fields = ('worker__sicil_no', 'worker__name_surname')
