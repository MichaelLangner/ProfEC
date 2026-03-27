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

from message_db.views import MessageListView
from message_db.views import delete_message
from message_db.views import MessageCreateView

urlpatterns = [
    path("", MessageListView.as_view(), name="message_db_root"),
    path("create/",MessageCreateView.as_view(),name="create_message"),
    path("message_list/", MessageListView.as_view(), name="message_list"),
    path("message_list/delete/<int:message_id>/", delete_message, name="delete_message"),

    
]




