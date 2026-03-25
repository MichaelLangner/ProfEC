

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError

from message_db.models import Message_DB

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import exceptions

from file_db.throttles import UploadThrottle   

# Create your views here.
class MessageCreateView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    throttle_classes = [UploadThrottle]
    login_url = "/accounts/login/"

    def handle_exception(self, exc):
        # Unauthenticated → hybrid behavior
        if isinstance(exc, exceptions.NotAuthenticated):
            if self.request.accepted_renderer.format == "html":
                return redirect(self.login_url)
            return Response({"detail": "Authentication required"}, status=401)
        return super().handle_exception(exc)

    def get(self, request):
        # Browser GET → show upload form
        if request.accepted_renderer.format == "html":
            return render(request, "create.html")
        # API GET → not allowed
        return Response({"detail": "Use POST to send message"}, status=405)

    def post(self, request):
        # Clear old messages for browser
        storage = get_messages(request)
        storage.used = True

        message = request.POST.get("message")
        if not message:
            if request.accepted_renderer.format == "html":
                #message.error(request, "No message provided.")
                return render(request, "create.html")
            return Response({"error": "No message provided"}, status=400)

        instance = Message_DB(
            message_owner=request.user,
            message_recipient=None,
            message_created=timezone.now(),
            message_deleted=None,
            message_topic=request.data.get("topic",""),
            message_text=request.data.get("message",""),
        )


        try:
            instance.full_clean()
            instance.save()

            # Browser success
            if request.accepted_renderer.format == "html":
                messages.success(request, "Message send")
                return redirect("message_list")

            # API success
            return Response({
                "id": str(instance.pk),
                "message_owner": instance.message_owner,
                "message_recipient": instance.message_recipient,
                "message_created": instance.message_created,
                "message_deleted": instance.message_deleted,
                "message_topic": instance.message_topic,
                "message_text": instance.message_text,
            }, status=201)

        except ValidationError as e:
            print("VALIDATION ERROR:", e.message_dict)
            if request.accepted_renderer.format == "html":
                messages.error(request, e.messages[0])
                return render(request, "create.html")

            return Response({"error": e.messages[0]}, status=400)
        
class MessageListView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    login_url = "/accounts/login/"

    def handle_exception(self, exc):
        # If user is not authenticated
        if isinstance(exc, exceptions.NotAuthenticated):
            # Browser → redirect to login page
            if self.request.accepted_renderer.format == "html":
                return redirect(self.login_url)

            # API client → JSON 401
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=401
            )

        return super().handle_exception(exc)

    def get(self, request):
        user = request.user
        query = request.GET.get("q", "").strip()
        date_from = request.GET.get("date_from", "")
        date_to = request.GET.get("date_to", "")

        # Base queryset depending on permissions
        if user.is_superuser or user.is_staff:
            messages = Message_DB.objects.filter(message_deleted__isnull=True)
        else:
            messages = Message_DB.objects.filter(
                Q(message_owner=user,time_deleted__isnull=True) |
                Q(message_recipient=user,time_deleted__isnull=True)
                )

        # Apply search filter if query exists
        if query:
            messages = messages.filter(
                Q(message_owner__username__icontains=query) |
                Q(message_recipient__username__icontains=query) |
                Q(message_created__icontains=query) |
                Q(message_deleted__icontains=query) |
                Q(message_topic__icontains=query) |
                Q(message_text__icontains=query)
            )

        if date_from:
            messages = messages.filter(message_create__date__gte=date_from)

        if date_to:
            messages = messages.filter(message_create__date__lte=date_to)

        messages = messages.order_by("-message_created")

        # Browser → HTML template
        if request.accepted_renderer.format == "html":
            return Response({"messages": messages}, template_name="message_list.html")

        # API client → JSON
        return Response({
            "messages": [
                {
                    #"id": m.id,
                    "message_owner": m.message_owner,
                    "message_recipient": m.message_recipient,
                    "message_created": m.message_created,
                    "message_topic": m.message_topic,
                    "message_text": m.message_text,
                }
                for m in messages
            ]
        })
    
@login_required
def delete_message(request, message_id):
    message_obj = get_object_or_404(Message_DB, id=message_id)
    #check permission
    user = request.user
    # Superusers and staff can delete anything
    if not (user.is_superuser or user.is_staff):
        # Normal users can only delete their own files
        if message_obj.message_owner != user:
            return HttpResponseForbidden("You do not have permission to delete this file.")



    # mark as deleted
    message_obj.message_deleted = timezone.now()
    message_obj.save(update_fields=["message_deleted"])

    messages.success(request, "Message deleted.")
    return redirect("message_list")