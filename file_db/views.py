from django.shortcuts import render

# for login/logout
from django.contrib.auth.decorators import login_required # type: ignore

# for upload
from django.utils import timezone
from file_db.models import File_DB
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
import os
from django.db.models import Q
import json


def file_info(request, pk):
    file_obj = get_object_or_404(File_DB, pk=pk)

    # Permission check
    user = request.user
    if not (user.is_superuser or user.is_staff):
        if file_obj.owner != user:
            return HttpResponseForbidden("You do not have permission to view this file.")

    if request.method == "POST":
        # Update editable fields
        file_obj.description = request.POST.get("description", "")
        file_obj.tags = request.POST.get("tags", "")
        file_obj.save()

        # Redirect back to the same page after saving
        return redirect("file_info", pk=pk)

    return render(request, "file_info.html", {"file": file_obj})

@login_required
def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"]

        stored = File_DB.objects.create(
            file=f,
            original_file_name=f.name,
            
            file_size=f.size,
            mimetype=f.content_type,

            time_upload=timezone.now(),  
            time_deleted=None,
            owner=request.user,

            tags=request.POST.get("tags", ""),
            access_customer = True,
            access_staff = True,
            access_super = True,
            description=request.POST.get("description", "")
        )
        print("Saved to:", stored.file.path)

        return redirect("file_list")

    return render(request, "upload.html")

@login_required
def delete_file(request, folder_name, file_name):

    render(request, "delete_file.html", {
            "folder_name": folder_name,
            "file_name": file_name,
        })
    
@login_required
def admin_download(request, pk):
    obj = get_object_or_404(File_DB, pk=pk)

    # Block deleted files
    if obj.time_deleted:
        raise Http404("File has been deleted")

    return FileResponse(
        obj.file.open("rb"),
        as_attachment=True,
        filename=obj.original_file_name
    )

@login_required
def file_list(request):
    user = request.user

    if user.is_superuser or user.is_staff:
        files = File_DB.objects.filter(time_deleted__isnull=True).order_by('-time_upload')
    else:
       files = File_DB.objects.filter(owner=user)
    
    # Add displayability flag to each file
    for f in files:
        f.is_displayable = can_inline(f.mimetype)
        f.is_plotable = can_plot(f.mimetype)
        f.basename = os.path.basename(f.file.name)

    return render(request, "file_list.html", {"files": files})




def file_list(request):
    user = request.user
    query = request.GET.get("q", "").strip()
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    
    # Base queryset depending on permissions
    if user.is_superuser or user.is_staff:
        files = File_DB.objects.filter(time_deleted__isnull=True)
    else:
        files = File_DB.objects.filter(owner=user)

    # Apply search filter if query exists
    if query:
        files = files.filter(
            Q(original_file_name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(mimetype__icontains=query) |
            Q(owner__username__icontains=query)
            
        )

    # Date range filtering
    if date_from:
        files = files.filter(time_upload__date__gte=date_from)

    if date_to:
        files = files.filter(time_upload__date__lte=date_to)

    # Order after filtering
    files = files.order_by("-time_upload")

    # Add displayability flag to each file
    for f in files:
        f.is_displayable = can_inline(f.mimetype)
        f.is_plotable = can_plot(f.mimetype)
        f.basename = os.path.basename(f.file.name)

    return render(request, "file_list.html", {"files": files})

@login_required
def delete_file(request, pk):
    file_obj = get_object_or_404(File_DB, pk=pk)
    #check permission
    user = request.user
    # Superusers and staff can delete anything
    if not (user.is_superuser or user.is_staff):
        # Normal users can only delete their own files
        if file_obj.owner != user:
            return HttpResponseForbidden("You do not have permission to delete this file.")

    # delete file from disk
    if file_obj.file:
        file_obj.file.delete(save=False)

    # clear the file path so Django admin knows it's gone
    file_obj.file = None

    # mark as deleted
    file_obj.time_deleted = timezone.now()
    file_obj.save(update_fields=["file", "time_deleted"])

    messages.success(request, "File deleted.")
    return redirect("file_list")

@login_required
def show_file(request, pk):
    file_obj = get_object_or_404(File_DB, pk=pk)

    # Security check
    user = request.user
    if not (user.is_superuser or user.is_staff):
        if file_obj.owner != user:
            return HttpResponseForbidden("You do not have permission to view this file.")

    # Determine MIME type and add text/csv as displayable
    mime_type=file_obj.mimetype
    if (mime_type=='text/csv'):
        mime_type='text/plain'
    # Extract original filename
    original_name = os.path.basename(file_obj.file.name)

    # Return inline preview
    response = FileResponse(open(file_obj.file.path, "rb"), content_type=mime_type)
    response["Content-Disposition"] = f"inline; filename={original_name}"
    return response

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

PLOTABLE_MIME_TYPES = {
    "text/csv",
}

def can_inline(mime):
    if mime is None:
        return False
    return any(mime.startswith(t) for t in DISPLAYABLE_MIME_TYPES)

def can_plot(mime):
    if mime is None:
        return False
    return any(mime.startswith(t) for t in PLOTABLE_MIME_TYPES)


@login_required
def info_file(request, pk):
    file_obj = get_object_or_404(File_DB, pk=pk)
    file_obj.basename = os.path.basename(file_obj.file.name)
    file_obj.is_displayable = can_inline(file_obj.mimetype)
    # Permission check
    user = request.user
    if not (user.is_superuser or user.is_staff):
        if file_obj.owner != user:
            return HttpResponseForbidden("You do not have permission to view this file.")

    if request.method == "POST":
        # Update editable fields
        file_obj.description = request.POST.get("description", "")
        file_obj.tags = request.POST.get("tags", "")
        file_obj.save()

        # Redirect back to the same page after saving
        return redirect("info_file", pk=pk)

    return render(request, "file_info.html", {"file": file_obj})

@login_required
def download_file(request, pk):
    file_obj = get_object_or_404(File_DB, pk=pk)

    # Permission check
    user = request.user
    if not (user.is_superuser or user.is_staff):
        if file_obj.owner != user:
            return HttpResponseForbidden("You do not have permission to download this file.")

    # Extract original filename
    original_name = os.path.basename(file_obj.file.name)

    # Force download
    response = FileResponse(open(file_obj.file.path, "rb"), content_type=file_obj.mimetype)
    response["Content-Disposition"] = f'attachment; filename="{original_name}"'
    return response


@login_required
def plot_file(request, pk):
    file_obj = get_object_or_404(File_DB, pk=pk)

    # Permission check
    user = request.user
    if not (user.is_superuser or user.is_staff):
        if file_obj.owner != user:
            return HttpResponseForbidden("You do not have permission to download this file.")

 
    # read file
    with open(file_obj.file.path, "r", encoding="utf-8") as f:
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
        title_json=json.dumps(file_obj.original_file_name)
    
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
        title_json=json.dumps(file_obj.original_file_name+' data structure not recognized')

        data_x=[]
        data_x_json=json.dumps(data_x)       
        
        data_y=[]
        data_y_json=json.dumps(data_y)
    

    # return header and data
    return render(request, "file_plot.html", {
            "header_x_json": header_x_json,
            "header_y_json": header_y_json,
            "data_x_json": data_x_json,
            "data_y_json": data_y_json,
            "title_json": title_json,

        })


    




