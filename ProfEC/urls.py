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
from django.contrib import admin 
from django.contrib.auth.views import LogoutView 
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import path, include


urlpatterns = [
    path(
        "admin/logout/",
            LogoutView.as_view(
            template_name="admin/logout.html",
            next_page="/admin/login/"
        ),
        name="admin-logout"
    ),
    path('admin/', admin.site.urls),

    path("", lambda request: redirect("file_db_root"), name="index"),

    path('accounts/', include('accounts.urls')),
    path('dashboards/', include('dashboards.urls')),
    path('files/', include('files.urls')),
    path('file_db/', include('file_db.urls')),
    path('message_db/',include('message_db.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
