from django.db import models

from utils.models import BaseModel


class PhoneNumber(BaseModel):
    creator = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="phone_number_creator",
    )
    label = models.CharField(max_length=50, blank=True, null=True)
    number = models.CharField(max_length=20, unique=True)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    last_recharged_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.number} - {self.credit} credit"
