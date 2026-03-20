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

from file_db.views import upload_file
from file_db.views import admin_download
from file_db.views import file_list
from file_db.views import delete_file
from file_db.views import show_file
from file_db.views import info_file
from file_db.views import download_file
from file_db.views import plot_file

urlpatterns = [
    path("", file_list, name="file_db_root"),
    path("upload/",upload_file,name="upload_file"),
    path("admin-download/<uuid:pk>/", admin_download, name="admin_download"),
    path("file_list/", file_list, name="file_list"),
    path("file_list/delete/<uuid:pk>/", delete_file, name="delete_file"),
    path("file_list/show/<uuid:pk>/", show_file, name="show_file"),
    path("file_list/info/<uuid:pk>/", info_file, name="info_file"),
    path("file_list/download/<uuid:pk>/", download_file, name="download_file"),
    path("file_list/plot/<uuid:pk>",plot_file,name="plot_file"),
]




