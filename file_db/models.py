from django.db import models

from file_db.utils import upload_to_uuid7
from file_db.storage import ProtectedStorage
import uuid
from accounts.models import User

protected_storage = ProtectedStorage()

class File_DB(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False) # id for the database contains only the uuid
    file = models.FileField(upload_to=upload_to_uuid7,storage=protected_storage, editable=False) # path of the file. file+extension

    original_file_name = models.CharField(max_length=256) # detected during upload
    file_size = models.PositiveBigIntegerField() # detected during upload
    mimetype = models.CharField(max_length=256) # detected during upload

    time_upload = models.DateTimeField(null=True, blank=True)  
    time_deleted = models.DateTimeField(null=True, blank=True) 

    owner = models.ForeignKey(User, on_delete=models.CASCADE) # detected during upload

    tags = models.TextField(max_length=256) # given by used; editable
    
    # access modes
    access_customer = models.BooleanField() # customer uploaded the file, but it is shown only to him and staff and not to other customers otherwise visible to all customers staff and supers
    access_staff = models.BooleanField() # is only shown to company staff not customers
    access_super = models.BooleanField() # is only available to super (logs/maintenace)
    
    description = models.TextField(blank=True) # add further information

    class Meta:
        verbose_name = "File_DB"
        verbose_name_plural = "Files_DB"

    def __str__(self):
        return self.original_file_name
    
