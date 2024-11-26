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

    @property
    def remaining_annual_leave_days(self):
        return self.annual_leave_days - self.used_leave_days


class WorkLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='attendance_records')
    check_in = models.DateTimeField(null=True, blank=True)  # user checkin time
    check_out = models.DateTimeField(null=True,
                                     blank=True)  # user checkout time
    date = models.DateField(auto_now_add=True)  # date of the record

    def __str__(self):
        return f"{self.employee.username} - {self.date}"


class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='leave_records')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]
    status = models.CharField(max_length=10, choices=status_choices,
                              default='pending')
    description = models.TextField()
    substitute = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                   related_name='substitute', null=True,
                                   blank=True)

    def __str__(self):
        return f"{self.created_at} - {self.employee.username} - {self.start_date} - {self.end_date}"
