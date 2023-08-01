from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class payment_master(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    created_on = models.DateTimeField(null=False,blank=False)
    amount = models.TextField(default="")
    requested_checksum = models.TextField(default="")
    responsed_checksum = models.JSONField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
