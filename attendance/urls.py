from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_dashboard, name='dashboard'),
    path('check-in-out/', views.check_in_out, name='check_in_out'),
    path('break/', views.break_management, name='break_management'),
    path('report/', views.attendance_report, name='report'),
    path('register-fingerprint/', views.register_fingerprint, name='register_fingerprint'),
] 