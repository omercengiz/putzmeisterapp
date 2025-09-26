from django.urls import path
from . import views

app_name = 'benefits'

urlpatterns = [
    path('', views.benefit_list, name='list'),                
    path('create/', views.benefit_create, name='create'),
    path('<int:pk>/edit/', views.benefit_update, name='update'),
    path('<int:pk>/delete/', views.benefit_delete, name='delete'),
    path("bulk/", views.benefit_bulk, name="bulk"), 
]
