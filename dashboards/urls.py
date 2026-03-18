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

from django.urls import path 

from dashboards.views import dashboard_auth
from dashboards.views import dashboard_admin
from dashboards.views import dashboard_customer

urlpatterns = [
    path("dashboard_auth/", dashboard_auth, name="dashboard_auth"),
    path("dashboard_admin/", dashboard_admin, name="dashboard_admin"),
    path("dashboard_customer/", dashboard_customer, name="dashboard_customer"),
]


