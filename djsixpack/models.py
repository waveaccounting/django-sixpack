from django.db import models


class SixpackParticipant(models.Model):
    experiment_name = models.CharField(max_length=255, db_index=True)
    unique_attr = models.CharField(max_length=255, db_index=True)
    converted = models.BooleanField(default=False)
    bucket = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
