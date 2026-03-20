import uuid
import os

def upload_to_uuid7(instance, filename):
    ext = os.path.splitext(filename)[1]  # keep original extension
    return f"upload/{uuid.uuid7()}{ext}"