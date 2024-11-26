from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import time
from django.utils.datetime_safe import datetime
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Create your views here.

from django.views.generic import TemplateView, ListView
from rest_framework.generics import UpdateAPIView

from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from application.forms import LoginForm, StaffLeaveRequestForm, \
    ManagerLeaveRequestForm
from application.models import WorkLog, Leave, Employee
from application.serializers import LoginSerializer
from django.utils.timezone import make_aware, now
from datetime import datetime, time, timedelta
from django.db.models import Sum, F, ExpressionWrapper, fields


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['username'] = user.username
            context['is_staff'] = user.is_staff
            context['is_manager'] = user.is_manager
        return context

    def get_late_minutes(self, obj):
        if obj.check_in:
            # work start time is 08:00
            work_start_time = datetime.combine(obj.date, time(8, 0))
            if obj.check_in > work_start_time:
                late_duration = obj.check_in - work_start_time
                return late_duration.seconds // 60  # changed to minutes
        return 0  # if is not late, return 0


class LoginView(APIView):

    def get(self, request, user_type, *args, **kwargs):
        # if user is already authenticated, redirect to dashboard or
        # not redirect to user_type login page
        if request.user.is_authenticated:
            return redirect('application:dashboard')
        if user_type == "manager":
            template_name = 'login_manager.html'
        elif user_type == "staff":
            template_name = 'login_staff.html'
        else:
            return redirect('application:dashboard')
        form = LoginForm()
        return render(request, template_name, context={'form': form})

    def post(self, request, user_type, *args, **kwargs):
        serializer = LoginSerializer(data=request.data,
                                     context={'user_type': user_type})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            login(request, validated_data["user"])  # log in user
            return redirect('application:dashboard')
        # if serializer is not valid, return errors
        form = LoginForm()
        return render(request, f'login_{user_type}.html',
                      context={'form': form, 'errors': serializer.errors})


class LogoutView(APIView):
    def get(self, request):
        logout(request)  # log out user
        return redirect('application:dashboard')


class LeaveRequestView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('application:dashboard')
        elif request.user.is_manager:
            template_name = 'manager-leave-request.html'
            form = ManagerLeaveRequestForm(request=request)
        else:
            form = StaffLeaveRequestForm(request=request)
            template_name = 'staff-leave-request.html'

        return render(request, template_name, context={'form': form})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('application:dashboard')
        elif request.user.is_manager:
            form = ManagerLeaveRequestForm(request.POST, request=request)
        else:
            form = StaffLeaveRequestForm(request.POST, request=request)

        if form.is_valid():
            form.save()
        print(form.errors)
        return redirect('application:dashboard')


class LeaveRequestAPIView(LoginRequiredMixin, ListView, UpdateAPIView):
    model = Leave
    template_name = 'staff-leaves.html'
    context_object_name = 'leave_requests'

    def get_queryset(self):
        if self.request.user.is_manager:
            return Leave.objects.all().order_by('created_at')
        return Leave.objects.filter(employee=self.request.user).order_by(
            'created_at')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('application:dashboard')
        return super().get(request, *args, **kwargs)

    @method_decorator(csrf_exempt)
    def patch(self, request, *args, **kwargs):
        if not request.user.is_manager:
            return HttpResponseForbidden("Bu işlem için yetkiniz yok.")

        leave_id = kwargs.get('pk')
        leave = get_object_or_404(Leave, pk=leave_id)
        new_status = request.data.get('action')

        if new_status not in ['pending', 'approved', 'rejected']:
            return HttpResponseForbidden("Geçersiz bir durum değeri.")
        leave.status = new_status
        leave.save()

        return Response(status=200)


class LateComersListView(ListView):
    model = WorkLog
    template_name = 'late_comers.html'
    context_object_name = 'late_comers'
    serializer_class = WorkLog

    def get_queryset(self):
        # Set expected check-in time (08:00)
        expected_check_in_time = make_aware(
            datetime.combine(now().date(), time(8, 0))
        )
        late_comers = WorkLog.objects.filter(
            check_in__isnull=False,  # Giriş yapmış olanlar
            check_in__gt=expected_check_in_time
            # Beklenen saatten sonra giriş yapanlar
        ).select_related('employee').exclude(employee__role='manager')

        # Calculate lateness duration
        for record in late_comers:
            record.late_by = record.check_in - expected_check_in_time


        return late_comers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            'expected_check_in_time'] = "08:00"  # to show in template
        return context

class MonthlyWorkLogView(ListView):
    model = WorkLog
    template_name = 'monthly_work_log.html'
    context_object_name = 'work_logs'

    def get_queryset(self):
        date_now = datetime.now()
        work_logs = WorkLog.objects.filter(
            check_in__month=date_now.month,
            check_in__year=date_now.year,
        ).annotate(
            work_duration=ExpressionWrapper(
                F('check_out') - F('check_in'),
                output_field=fields.DurationField()
            )
        )

        summary = (
            work_logs.values('employee__username')
            .annotate(total_duration=Sum('work_duration'))
            .order_by('employee__username')
        )
        if self.request.user.is_staff:
            summary = summary.filter(employee=self.request.user)

        return summary

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_now = datetime.now()
        context['month'] = date_now.month
        context['year'] = date_now.year
        return context