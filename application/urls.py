from django.urls import path
from .views import LoginView, LogoutView, DashboardView

app_name = "application"

urlpatterns = [
    path('login/<str:user_type>', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
