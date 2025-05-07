from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ReportType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    frequency_choices = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]
    frequency = models.CharField(max_length=10, choices=frequency_choices)
    format_choices = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('both', 'Both'),
    ]
    default_format = models.CharField(max_length=5, choices=format_choices, default='pdf')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ReportSchedule(models.Model):
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_recipients = models.TextField(help_text="Comma-separated list of email addresses")
    schedule_time = models.TimeField()
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.report_type.name} - {self.user.username}"

class ReportHistory(models.Model):
    report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255)
    format = models.CharField(max_length=5, choices=ReportType.format_choices)
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ])
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.report_type.name} - {self.generated_at}"
