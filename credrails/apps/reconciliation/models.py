from django.db import models


class ReconciliationStatus(models.TextChoices):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    PROCESSED = "PROCESSED"
    SCHEDULED = "SCHEDULED"
    INPROGRESS = "INPROGRESS"


class Reconciliation(models.Model):
    source = models.FileField(upload_to="reconciliation/source/")
    target = models.FileField(upload_to="reconciliation/target/")
    status = models.CharField(max_length=100, choices=ReconciliationStatus, default=ReconciliationStatus.PENDING)
