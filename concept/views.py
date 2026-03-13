from django.shortcuts import render

# Create your views here.
# for login/logout
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib.auth.decorators import user_passes_test # type: ignore

# for fileviewer
from pathlib import Path
from django.conf import settings
from django.http import HttpResponseForbidden
from django.http import FileResponse
from django.http import Http404

#adjusting my custom signup dialog to include more parameters
from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group


# define decorators
def group_required(group_name):
    return user_passes_test(lambda user: user.is_authenticated and user.groups.filter(name=group_name).exists())

def groups_required(*group_names):
    def check(user):
        return user.is_authenticated and user.groups.filter(name__in=group_names).exists()
    return user_passes_test(check)



# signup replacement 
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # assign group
            customer_group = Group.objects.get(name="customer")
            user.groups.add(customer_group)

            return redirect("login")
    else:
        form = CustomUserCreationForm()
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

# restricted file serving on index.html formally known as file browser

def index(request, folder_name=None):
    user = request.user
    base: Path = settings.PRIVATE_STORAGE_ROOT

    # Determine which folders the user can see
    folders = []

    general_path = base / "General"
    if general_path.is_dir():
        folders.append(("General", general_path))

    user_folder = f"{user.id}_{user.username}"
    user_path = base / user_folder
    if user_path.is_dir():
        folders.append((user_folder, user_path))

    if user.is_superuser or request.user.groups.filter(name="admin").exists():
        for path in base.iterdir():
            if path.is_dir() and path.name not in [f[0] for f in folders]:
                folders.append((path.name, path))

    # If a folder is selected, list its files
    files = []
    if folder_name:
        folder_path = base / folder_name

        # Permission check
        if not (user.is_superuser or request.user.groups.filter(name="admin").exists()) and folder_name != "General":
            owner_id = int(folder_name.split("_")[0])
            if owner_id != user.id:
                return HttpResponseForbidden("Not allowed")

        files = [f.name for f in folder_path.iterdir() if f.is_file()]

    return render(request, "index.html", {
        "folders": folders,
        "selected_folder": folder_name,
        "files": files,
    })



@login_required
def private_file(request, folder_name, file_name):
    user = request.user
    base: Path = settings.PRIVATE_STORAGE_ROOT

    folder_path = base / folder_name
    file_path = folder_path / file_name

    # Permission check 
    if not (user.is_superuser or request.user.groups.filter(name="customer").exists()) and folder_name != "General":
        # alternative for multiple groups: request.user.groups.filter(name__in=["admin", "customer"]).exists()
        owner_id = int(folder_name.split("_")[0])
        if owner_id != user.id:
            return HttpResponseForbidden("Not allowed")

    # File exists?
    if not file_path.exists() or not file_path.is_file():
        raise Http404("File not found")

    # Return file as download
    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=file_name
    )




