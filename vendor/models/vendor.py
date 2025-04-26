from django.db import models
from rest_framework.exceptions import ValidationError

from utils.models import BaseModel


class Vendor(BaseModel):
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="vendors",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if self.balance < 0:
            raise ValueError("Balance cannot be negative")

        if self.is_active:
            # Exclude self if updating an existing record
            if (
                Vendor.objects.filter(user=self.user, is_active=True)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError("User can have only one active vendor.")

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
