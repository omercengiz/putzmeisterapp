from django.contrib import admin
from django.urls import path
from . import views
from .views import user_permission_dashboard, update_user_role, create_user


app_name = "user"


urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('permissions/', user_permission_dashboard, name='user_permission_dashboard'),
    path('permissions/<int:user_id>/update/', update_user_role, name='update_user_role'),
    path('permissions/create/', create_user, name='create_user'),
    path('permissions/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]
