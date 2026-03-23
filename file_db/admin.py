from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from file_db.models import File_DB
from django.contrib.admin.utils import NestedObjects
from django.db import router
import os
from collections import Counter

@admin.register(File_DB)
class FileDBAdmin(admin.ModelAdmin):
    readonly_fields = (
        "file_link",
        "id",
        "time_upload",
        "original_file_name",
        "file_size",
        "mimetype",
        "time_deleted",
        "owner",
    )


    fields = (
        "file_link",        # read‑only, shown first
        "original_file_name",    # read‑only
        "file_size",        # read‑only
        "mimetype",         # read‑only
        "owner",         # read‑only
        "time_upload",      # read‑only
        "time_deleted",     # read‑only
        "tags",             # editable
        "access_any",
        "access_customer",  # editable
        "access_staff",     # editable
        "access_super",     # editable
        "description",      # editable
    )

    list_display = (
        "id",
        "original_file_name",
        "file_link",
        "time_upload",
        "file_size",
        "mimetype",
        "time_deleted",
        "owner",
        "tags",
        "access_any",
        "access_customer",
        "access_staff",
        "access_super",
        "description",
    )

    def file_link(self, obj):
        if obj.time_deleted:
            return "(deleted)"
        url = reverse("admin_download", args=[obj.pk])
        return format_html('<a href="{}">Download file</a>', url)
    
    file_link.short_description = "File"
    

    # delete the file and make admin recognise it : the second part does not work properly, because the FileField can not be properly cleaned
    def get_deleted_objects(self, objs, request):
        using = router.db_for_write(self.model)
        collector = NestedObjects(using=using)
        collector.collect(objs)

        # Django's nested delete structure
        to_delete = collector.nested()
        protected = collector.protected

        # Build model_count manually
        model_count = Counter()
        for model, objects in collector.data.items():
            model_count[model._meta.verbose_name_plural] += len(objects)

        # Required by your Django version
        perms_needed = set()

        # Remove file deletion warnings if the file does not exist
        for obj in objs:
            if hasattr(obj, "file"):
                if not obj.file or not obj.file.name:
                    # No file → remove from delete list
                    self._remove_file_from_nested(to_delete, obj.file)
                    continue

                if not os.path.exists(obj.file.path):
                    # File missing → remove from delete list
                    self._remove_file_from_nested(to_delete, obj.file)

        return to_delete, model_count, perms_needed, protected

    def _remove_file_from_nested(self, nested, file_obj):
        """Recursively remove the file object from Django's nested delete list."""
        if isinstance(nested, list):
            for item in list(nested):
                if item == file_obj:
                    nested.remove(item)
                else:
                    self._remove_file_from_nested(item, file_obj)
    
    def delete_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['deleted_file_notice'] = "This entry has no file attached."
        return super().delete_view(request, object_id, extra_context)
