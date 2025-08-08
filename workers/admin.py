from django.contrib import admin
from .models import Workers
from .lookups import (
    Group, ShortClass, DirectorName, Currency,
    WorkClass, ClassName, Department, CostCenter
)


# Register your models here.
@admin.register(Workers)
class WorkersAdmin(admin.ModelAdmin):
    list_display = ["sicil_no","name_surname", "author", "created_date"]
    list_display_links = ["sicil_no", "name_surname", "author", "created_date"]
    search_fields = ["sicil_no"]
    list_filter = ["created_date"]
    class Meta:
        model = Workers


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ShortClass)
class ShortClassAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(DirectorName)
class DirectorNameAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code']
    search_fields = ['code']

@admin.register(WorkClass)
class WorkClassAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ClassName)
class ClassNameAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']