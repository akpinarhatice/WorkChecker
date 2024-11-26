from django.urls import path
from .views import LoginView, LogoutView, DashboardView, \
    LeaveRequestView, LeaveRequestAPIView, LateComersListView, \
    MonthlyWorkLogView

app_name = "application"

urlpatterns = [
    path('login/<str:user_type>', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('leave-request/', LeaveRequestView.as_view(), name='leave_request'),
    path('staff-leaves', LeaveRequestAPIView.as_view(),
         name='staff_leaves'),
    path('staff-leaves/<int:pk>/update-status/', LeaveRequestAPIView.as_view(),
         name='update_leave_status'),
    path('late-comers/', LateComersListView.as_view(), name='late-comers'),
    path('monthly-report/', MonthlyWorkLogView.as_view(),
         name='monthly_report'),
]
