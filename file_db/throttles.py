from rest_framework.throttling import UserRateThrottle

class UploadThrottle(UserRateThrottle):
    scope = "uploads"