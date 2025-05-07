from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('generate/<int:report_type_id>/', views.generate_report, name='generate_report'),
    path('schedule/<int:report_type_id>/', views.schedule_report, name='schedule_report'),
    path('dashboard/', views.dashboard, name='dashboard'),
] 