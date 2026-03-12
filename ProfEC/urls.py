"""
URL configuration for ProfEC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path 

from django.contrib.auth import views as auth_views 
from django.contrib.auth.views import LogoutView 
from concept.views import index
from concept.views import signup
from concept.views import dashboard_auth
from concept.views import dashboard_admin
from concept.views import dashboard_customer

from concept.views import private_file


urlpatterns = [
    path(
        "admin/logout/",
        auth_views.LogoutView.as_view(
            template_name="admin/logout.html",
            next_page="/admin/login/"
        ),
        name="admin-logout"
    ),
    path('admin/', admin.site.urls),
    
    path("signup/", signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="logout.html"), name="logout"),
    path("dashboard_auth/", dashboard_auth, name="dashboard_auth"),
    path("dashboard_admin/", dashboard_admin, name="dashboard_admin"),
    path("dashboard_customer/", dashboard_customer, name="dashboard_customer"),

    path('',index,name="index"),
    
    path("<str:folder_name>/", index, name="index_folder"),
    path("<str:folder_name>/<str:file_name>/",private_file,name="private_file"),

    
]
