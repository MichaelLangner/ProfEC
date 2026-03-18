from django.shortcuts import render

# for login/logout
from django.contrib.auth.decorators import login_required # type: ignore
from concept.views import group_required
from concept.views import groups_required

# restricted areas
@login_required
def dashboard_auth(request):
    return render(request, "dashboard_auth.html")

@group_required("admin")
def dashboard_admin(request):
    return render(request, "dashboard_admin.html")

@groups_required("admin","customer")
def dashboard_customer(request):
    return render(request, "dashboard_customer.html")

