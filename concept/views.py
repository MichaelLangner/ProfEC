from django.shortcuts import render

# Create your views here.
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore

from django.contrib.auth.decorators import user_passes_test # type: ignore

# define decorators
def group_required(group_name):
    return user_passes_test(lambda user: user.is_authenticated and user.groups.filter(name=group_name).exists())

def groups_required(*group_names):
    def check(user):
        return user.is_authenticated and user.groups.filter(name__in=group_names).exists()
    return user_passes_test(check)


# landing page
def index(request):

    return render(request,"index.html")

# signup replacement 
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})

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