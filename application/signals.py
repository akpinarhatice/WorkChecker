# application/signals.py
import math
from datetime import datetime, time

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.template.defaulttags import now
from django.utils import timezone
from django.utils.timezone import make_aware

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

    worklogs = WorkLog.objects.filter(employee=user, check_in__isnull=False,
                                      check_out__isnull=False)
    used_leave_seconds = 0

    for worklog in worklogs:
        expected_check_in_time = make_aware(
            datetime.combine(worklog.date, time(8, 0))
        )
        late_by = worklog.check_in - expected_check_in_time
        if late_by.total_seconds() > 0:
            used_leave_seconds += late_by.total_seconds()

    leaves = user.leave_records.filter(
        created_at__year=timezone.now().year, status='approved'
    )
    for leave in leaves:
        late_by = leave.end_date - leave.start_date
        if late_by.total_seconds() > 0:
            used_leave_seconds += late_by.total_seconds()

    user.used_leave_days = math.floor(used_leave_seconds // 86400)
    user.save()




@receiver(user_logged_out)
def update_worklog_on_logout(sender, request, user, **kwargs):
    worklog = WorkLog.objects.filter(employee=user, date=timezone.now().date(),
                                     check_out__isnull=True).first()
    if worklog:
        worklog.check_out = timezone.now()
        worklog.save()
