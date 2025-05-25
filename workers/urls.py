from django.contrib import admin
from django.urls import path
from . import views


app_name = "workers"


urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('addworkers/', views.AddWorkers, name="addworkers"),
    path('update/<int:id>', views.updateWorkers, name="updateworkers"),
    path('delete/<int:id>', views.deleteWorkers, name="deleteworkers"),
]
