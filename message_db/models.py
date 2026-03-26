from django.db import models
from accounts.models import User
# Create your models here.
class Message_DB(models.Model):
    
    
    message_owner=models.ForeignKey(User, on_delete=models.CASCADE,related_name='messages_sent',null=True, blank=True) 
    message_recipient=models.ForeignKey(User, on_delete=models.CASCADE,related_name='messages_received',null=True, blank=True) 

    message_created=models.DateTimeField(null=True, blank=True)
    message_deleted=models.DateTimeField(null=True, blank=True)
    
    message_topic = models.TextField(blank=False)
    message_text = models.TextField(blank=False)

    class Meta:
        verbose_name = "message_DB"
        verbose_name_plural = "messages_DB"

    def __str__(self):
        return ""