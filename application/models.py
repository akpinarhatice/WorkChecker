from django.db import models
from django.contrib.auth.models import AbstractUser


class Employee(AbstractUser):
    ROLE_CHOICES = [
        ('staff', 'Personel'),
        ('manager', 'Yetkili'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,
                            default='staff')
    position = models.CharField(max_length=50, null=True, blank=True)
    annual_leave_days = models.IntegerField(
        default=15)  # leave days
    used_leave_days = models.IntegerField(default=0)  # used leave days
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.role == 'staff'

    @property
    def is_manager(self):
        return self.role == 'manager'
