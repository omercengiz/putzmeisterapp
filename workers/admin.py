from django.contrib import admin
from .models import Workers


# Register your models here.
@admin.register(Workers)
class WorkersAdmin(admin.ModelAdmin):
    list_display = ["sicil_no","name_surname", "author", "created_date"]
    list_display_links = ["sicil_no", "name_surname", "author", "created_date"]
    search_fields = ["sicil_no"]
    list_filter = ["created_date"]
    class Meta:
        model = Workers
