from django.db import models
import uuid
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    currency = models.CharField(max_length=3, default='LKR') # e.g., LKR, INR
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Driver: {self.user.username}"


class Trip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='trips')
    fare_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(db_index=True) # Indexed for fast date-filtering
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.driver.user.username} - Fare: {self.fare_amount}"


class FuelFillUp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='fuel_logs')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    liters = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(db_index=True) # Indexed for fast date-filtering

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.driver.user.username} - Fuel: {self.cost}"