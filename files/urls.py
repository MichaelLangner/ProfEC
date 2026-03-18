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

from files.views import files

from files.views import download_file
from files.views import view_file
from files.views import plot_file

urlpatterns = [

    path("", files, name="files_root"),
    
    # Folder listing
    path("<str:folder_name>/", files, name="index_folder"),

    # File actions
    path("<str:folder_name>/<str:file_name>/download",download_file,name="download_file"),
    path("<str:folder_name>/<str:file_name>/view",view_file,name="view_file"),
    path("<str:folder_name>/<str:file_name>/plot",plot_file,name="plot_file"),
]
