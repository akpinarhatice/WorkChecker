# application/signals.py

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from application.models import WorkLog


@receiver(user_logged_in)
def create_worklog_on_login(sender, request, user, **kwargs):
    if not WorkLog.objects.filter(employee=user,
                                  date=timezone.now().date()).exists():
        WorkLog.objects.create(
            employee=user,
            check_in=timezone.now(),
            date=timezone.now().date()
        )


@receiver(user_logged_out)
def update_worklog_on_logout(sender, request, user, **kwargs):
    worklog = WorkLog.objects.filter(employee=user, date=timezone.now().date(),
                                     check_out__isnull=True).first()
    if worklog:
        worklog.check_out = timezone.now()
        worklog.save()
