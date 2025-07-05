from django.urls import path
from . import views

app_name = "benefits"

urlpatterns = [
    path("benefitsdashboard/", views.add_benefit, name="add_benefit"),
]
