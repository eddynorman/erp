from django.contrib import admin
from .models import AttendanceSettings, FingerprintTemplate, AttendanceRecord, AttendanceSummary

@admin.register(AttendanceSettings)
class AttendanceSettingsAdmin(admin.ModelAdmin):
    list_display = ('working_hours_start', 'working_hours_end', 'late_threshold_minutes', 
                   'early_leave_threshold_minutes', 'break_duration_minutes')
    list_editable = ('working_hours_start', 'working_hours_end', 'late_threshold_minutes',
                    'early_leave_threshold_minutes', 'break_duration_minutes')
    list_display_links = None  # This makes no fields clickable since all are editable

@admin.register(FingerprintTemplate)
class FingerprintTemplateAdmin(admin.ModelAdmin):
    list_display = ('employee', 'created_at', 'last_updated', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'last_updated')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time', 'attendance_type', 'status', 'fingerprint_verified')
    list_filter = ('attendance_type', 'status', 'fingerprint_verified', 'date')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'

@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in_time', 'check_out_time', 
                   'total_working_hours', 'status', 'is_late', 'is_early_leave')
    list_filter = ('status', 'is_late', 'is_early_leave', 'date')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
