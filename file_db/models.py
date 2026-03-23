from django.db import models

from file_db.utils import upload_to_uuid7
from file_db.storage import ProtectedStorage
import uuid
from accounts.models import User

# check file contents for cummon file types -> maybe replace with magic-library?
from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".txt", ".csv", ".pdf"}

def validate_file_type(file):
    name = file.name.lower()

    # --- 1. Check extension ---
    if not any(name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValidationError("Only .txt, .csv, and .pdf files are allowed.")

    # --- 2. Check PDF header ---
    header = file.read(5)
    file.seek(0)

    if name.endswith(".pdf"):
        if header != b"%PDF-":
            raise ValidationError("Invalid PDF file.")
        return

    # --- 3. Check UTF-8 text for txt/csv ---
    try:
        file.read().decode("utf-8")
        file.seek(0)
    except UnicodeDecodeError:
        file.seek(0)
        raise ValidationError("TXT and CSV files must be UTF‑8 encoded.")

    return

protected_storage = ProtectedStorage()

class File_DB(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False) # id for the database contains only the uuid
    file = models.FileField(upload_to=upload_to_uuid7,storage=protected_storage, editable=False,validators=[validate_file_type]) # path of the file. file+extension

    original_file_name = models.CharField(max_length=256) # detected during upload
    file_size = models.PositiveBigIntegerField() # detected during upload
    mimetype = models.CharField(max_length=256) # detected during upload

    time_upload = models.DateTimeField(null=True, blank=True)  
    time_deleted = models.DateTimeField(null=True, blank=True) 

    owner = models.ForeignKey(User, on_delete=models.CASCADE) # detected during upload

    tags = models.TextField(max_length=256,blank=True) # given by used; editable
    
    # access modes
    access_any = models.BooleanField(default=False) # visible for anybody
    access_customer = models.BooleanField(default=True) # customer uploaded the file, but it is shown only to him and staff and not to other customers otherwise visible to all customers staff and supers
    access_staff = models.BooleanField(default=False) # is only shown to company staff not customers
    access_super = models.BooleanField(default=False) # is only available to super (logs/maintenace)
    
    description = models.TextField(blank=True) # add further information

    class Meta:
        verbose_name = "File_DB"
        verbose_name_plural = "Files_DB"

    def __str__(self):
        return self.original_file_name
    
