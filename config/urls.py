"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from workers.views import index, manage_lookups, delete_lookup, update_lookup


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    path('workers/', include("workers.urls")),
    path('user/', include("user.urls")),
    path('benefits/', include('benefits.urls')),
    path("lookups/", manage_lookups, name="manage_lookups"),
    path("lookups/delete/<str:model_name>/<int:pk>/", delete_lookup, name="delete_lookup"),
    path("lookups/<str:model_name>/<int:pk>/update/", update_lookup, name="update_lookup"),

]
