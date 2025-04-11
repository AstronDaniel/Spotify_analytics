from django.db import models
from django.utils import timezone
from datetime import timedelta

class TemporaryModel(models.Model):
    valid_until = models.DateTimeField(default=timezone.now() + timedelta(hours=1))
