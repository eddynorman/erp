from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class AttendanceSettings(models.Model):
    """Global settings for attendance system"""
    working_hours_start = models.TimeField(help_text="Default start time for working hours")
    working_hours_end = models.TimeField(help_text="Default end time for working hours")
    late_threshold_minutes = models.IntegerField(
        default=15,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Minutes after which an employee is considered late"
    )
    early_leave_threshold_minutes = models.IntegerField(
        default=15,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Minutes before which an employee is considered leaving early"
    )
    break_duration_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(180)],
        help_text="Default break duration in minutes"
    )
    
    class Meta:
        verbose_name = "Attendance Settings"
        verbose_name_plural = "Attendance Settings"

    def __str__(self):
        return "Attendance Settings"

class FingerprintTemplate(models.Model):
    """Store employee fingerprint templates"""
    employee = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fingerprint')
    template_data = models.BinaryField(help_text="Encrypted fingerprint template data")
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Fingerprint for {self.employee.get_full_name()}"

class AttendanceRecord(models.Model):
    """Record employee attendance entries"""
    ATTENDANCE_TYPE_CHOICES = [
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('break_start', 'Break Start'),
        ('break_end', 'Break End'),
    ]

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('early_leave', 'Early Leave'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    fingerprint_verified = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']
        unique_together = ['employee', 'date', 'attendance_type']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} {self.time} ({self.attendance_type})"

class AttendanceSummary(models.Model):
    """Daily summary of employee attendance"""
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_summaries')
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    total_working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_break_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=AttendanceRecord.STATUS_CHOICES, default='present')
    is_late = models.BooleanField(default=False)
    is_early_leave = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['employee', 'date']
        verbose_name_plural = "Attendance Summaries"

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.status})"
