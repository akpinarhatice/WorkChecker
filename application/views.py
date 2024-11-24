from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

# Create your views here.

from django.views.generic import TemplateView, ListView
from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework.views import APIView

from application.forms import LoginForm, StaffLeaveRequestForm, \
    ManagerLeaveRequestForm
from application.models import WorkLog, Leave
from application.serializers import LoginSerializer


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('application:dashboard')
        return super().get(request, *args, **kwargs)


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
            return redirect('application:index')
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
        return redirect('application:login', user_type='staff')


class LeaveRequestView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('application:index')
        elif request.user.is_manager:
            template_name = 'manager_leave_request.html'
            form = ManagerLeaveRequestForm(request=request)
        else:
            form = StaffLeaveRequestForm(request=request)
            template_name = 'staff_leave_request.html'

        return render(request, template_name, context={'form': form})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('application:index')
        elif request.user.is_manager:
            form = ManagerLeaveRequestForm(request.POST, request=request)
        else:
            form = StaffLeaveRequestForm(request.POST, request=request)

        if form.is_valid():
            form.save()
        print(form.errors)
        return redirect('application:dashboard')


class LeaveRequestAPIView(LoginRequiredMixin, ListView):
    model = Leave
    template_name = 'staff_leaves.html'
    context_object_name = 'leave_requests'

    def get_queryset(self):
        return Leave.objects.filter(employee=self.request.user).order_by('created_at')
