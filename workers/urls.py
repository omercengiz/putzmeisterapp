from django.contrib import admin
from django.urls import path
from . import views


app_name = "workers"


urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('addworkers/', views.AddWorkers, name="addworkers"),
    path('update/<int:id>', views.updateWorkers, name="updateworkers"),
    path('delete/<int:id>', views.deleteWorkers, name="deleteworkers"),
    path("bulk-salaries/", views.bulk_set_gross_salaries, name="bulk_set_gross_salaries"),
    path("worker/<int:worker_id>/salaries/", views.list_worker_salaries, name="list_worker_salaries"),
    path("salary/<int:salary_id>/delete/", views.delete_salary_record, name="delete_salary_record"),
    path("salary/<int:salary_id>/delete/", views.delete_salary_record, name="delete_salary_record"),
    path("salary/<int:salary_id>/update/", views.update_salary_record, name="update_salary_record"),  
    path("import/", views.import_workers, name="import_workers"),
]