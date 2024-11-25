from django.urls import path
from .views import LoginView, LogoutView, DashboardView, IndexView, \
    LeaveRequestView, LeaveRequestAPIView

app_name = "application"

urlpatterns = [
    path('login/<str:user_type>', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', IndexView.as_view(), name='index'),
    path('leave-request/', LeaveRequestView.as_view(), name='leave_request'),
    path('staff_leaves', LeaveRequestAPIView.as_view(),
         name='staff_leaves'),
]
