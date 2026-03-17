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
import mimetypes

#adjusting my custom signup dialog to include more parameters
from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group

# for data
import json


# define decorators
def group_required(group_name):
    return user_passes_test(lambda user: user.is_authenticated and (user.groups.filter(name=group_name).exists() or user.is_superuser))

def groups_required(*group_names):
    def check(user):
        return user.is_authenticated and (user.groups.filter(name__in=group_names).exists() or user.is_superuser)
    return user_passes_test(check)

# index dummy
def index(request):
    return render(request,"index.html")

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
DISPLAYABLE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "text/plain",
    "text/csv",
    "application/pdf",
}

PLOTABLE_FILE_TYPES = {
    "csv",
}

def files(request, folder_name=None):
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

        #files = [f.name for f in folder_path.iterdir() if f.is_file()]
        mimetypes.add_type("text/csv", ".csv", strict=True)
        mimetypes.add_type("text/plain", ".csv", strict=False)
        for file in folder_path.iterdir():
            mime_type, _ = mimetypes.guess_type(str(file))
            

            files.append({
                "name": file.name,
                "displayable": mime_type in DISPLAYABLE_MIME_TYPES,
                "plotable": file.name.split(".")[1] in PLOTABLE_FILE_TYPES,
            })
            


    return render(request, "files.html", {
        "folders": folders,
        "selected_folder": folder_name,
        "files": files,
    })



@login_required
def download_file(request, folder_name, file_name):
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

@login_required
def view_file(request, folder_name, file_name):
    user = request.user
    base: Path = settings.PRIVATE_STORAGE_ROOT

    folder_path = base / folder_name
    file_path = folder_path / file_name

    # Permission check (unchanged)
    if not (user.is_superuser or request.user.groups.filter(name="customer").exists()) and folder_name != "General":
        owner_id = int(folder_name.split("_")[0])
        if owner_id != user.id:
            return HttpResponseForbidden("Not allowed")

    # File exists?
    if not file_path.exists() or not file_path.is_file():
        raise Http404("File not found")

    # Detect MIME type (important for inline display)
    mimetypes.add_type("text/csv", ".csv", strict=True)
    mimetypes.add_type("text/plain", ".csv", strict=False)
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type in ("text/csv", None): # force text/plain 
        mime_type = "text/plain"

    # Return file inline 
    return FileResponse(
        open(file_path, "rb"),
        as_attachment=False,  
        filename=file_name,
        content_type=mime_type or "text/plain" 
    )


@login_required
def plot_file(request, folder_name, file_name):
    user = request.user
    base: Path = settings.PRIVATE_STORAGE_ROOT

    folder_path = base / folder_name
    file_path = folder_path / file_name

    # Permission check (unchanged)
    if not (user.is_superuser or request.user.groups.filter(name="customer").exists()) and folder_name != "General":
        owner_id = int(folder_name.split("_")[0])
        if owner_id != user.id:
            return HttpResponseForbidden("Not allowed")

    # File exists?
    if not file_path.exists() or not file_path.is_file():
        raise Http404("File not found")
    # read file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # parse content
    lines = content.splitlines()
    l=len(lines)
    #check if filestructure is correct (always to comma seperated values in each line)
    ok=1
    for i in range(0,l):
        if (len(lines[i].split(","))!=2): 
            ok=0

    if (ok):
        header_x=lines[0].split(",")[0]
        header_y=lines[0].split(",")[1]
        header_x_json=json.dumps(header_x)
        header_y_json=json.dumps(header_y)
        title_json=json.dumps(file_name)
    
        data_x=[]
        for i in range(1,l):
            data_x.append(lines[i].split(",")[0])
        
        data_x_json=json.dumps(data_x)
        
        
        data_y=[]
        for i in range(1,l):
            data_y.append(lines[i].split(",")[1])
        
        data_y_json=json.dumps(data_y)
    else: # default if data structure is not recognized
        header_x='none'
        header_y='none'
        header_x_json=json.dumps(header_x)
        header_y_json=json.dumps(header_y)
        title_json=json.dumps(file_name+' data structure not recognized')

        data_x=[]
        data_x_json=json.dumps(data_x)       
        
        data_y=[]
        data_y_json=json.dumps(data_y)
    

    # return header and data
    return render(request, "plot_file.html", {
            "file_name": file_name,
            "folder_name": folder_name,
            "header_x_json": header_x_json,
            "header_y_json": header_y_json,
            "data_x_json": data_x_json,
            "data_y_json": data_y_json,
            "title_json": title_json,

        })

def try_float(v):
   
   try:
       return float(v)
   except Exception:
       return 'nan'

