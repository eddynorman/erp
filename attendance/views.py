from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import (
    AttendanceRecord, 
    AttendanceSummary, 
    FingerprintTemplate,
    AttendanceSettings
)
from datetime import datetime, timedelta
import json

@login_required
def attendance_dashboard(request):
    """Main attendance dashboard view"""
    today = timezone.now().date()
    
    # Get today's attendance record for the user
    today_record = AttendanceRecord.objects.filter(
        employee=request.user,
        date=today
    ).order_by('-time')
    
    # Get attendance summary for the current month
    month_start = today.replace(day=1)
    month_summary = AttendanceSummary.objects.filter(
        employee=request.user,
        date__gte=month_start,
        date__lte=today
    ).order_by('-date')
    
    context = {
        'today_record': today_record,
        'month_summary': month_summary,
        'today': today,
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
def check_in_out(request):
    """Handle check-in and check-out operations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fingerprint_verified = data.get('fingerprint_verified', False)
            location = data.get('location', '')
            
            # Get current time
            now = timezone.now()
            
            # Check if there's already a check-in for today
            today_record = AttendanceRecord.objects.filter(
                employee=request.user,
                date=now.date(),
                attendance_type='check_in'
            ).first()
            
            if today_record:
                # If already checked in, create check-out record
                if not AttendanceRecord.objects.filter(
                    employee=request.user,
                    date=now.date(),
                    attendance_type='check_out'
                ).exists():
                    AttendanceRecord.objects.create(
                        employee=request.user,
                        date=now.date(),
                        time=now.time(),
                        attendance_type='check_out',
                        fingerprint_verified=fingerprint_verified,
                        location=location
                    )
                    messages.success(request, 'Check-out recorded successfully!')
            else:
                # Create check-in record
                AttendanceRecord.objects.create(
                    employee=request.user,
                    date=now.date(),
                    time=now.time(),
                    attendance_type='check_in',
                    fingerprint_verified=fingerprint_verified,
                    location=location
                )
                messages.success(request, 'Check-in recorded successfully!')
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def break_management(request):
    """Handle break start and end operations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            break_type = data.get('break_type')  # 'start' or 'end'
            fingerprint_verified = data.get('fingerprint_verified', False)
            location = data.get('location', '')
            
            now = timezone.now()
            attendance_type = 'break_start' if break_type == 'start' else 'break_end'
            
            # Check if there's already a break record of the same type for today
            if AttendanceRecord.objects.filter(
                employee=request.user,
                date=now.date(),
                attendance_type=attendance_type
            ).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Break {break_type} already recorded for today'
                })
            
            # Create break record
            AttendanceRecord.objects.create(
                employee=request.user,
                date=now.date(),
                time=now.time(),
                attendance_type=attendance_type,
                fingerprint_verified=fingerprint_verified,
                location=location
            )
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def attendance_report(request):
    """Generate attendance reports"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    employee_id = request.GET.get('employee')
    
    query = Q()
    if start_date:
        query &= Q(date__gte=start_date)
    if end_date:
        query &= Q(date__lte=end_date)
    if employee_id:
        query &= Q(employee_id=employee_id)
    
    records = AttendanceRecord.objects.filter(query).order_by('-date', '-time')
    summaries = AttendanceSummary.objects.filter(query).order_by('-date')
    
    context = {
        'records': records,
        'summaries': summaries,
        'start_date': start_date,
        'end_date': end_date,
        'employee_id': employee_id,
    }
    return render(request, 'attendance/report.html', context)

@login_required
def register_fingerprint(request):
    """Handle fingerprint registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            template_data = data.get('template_data')
            
            if not template_data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No fingerprint template data provided'
                })
            
            # Create or update fingerprint template
            FingerprintTemplate.objects.update_or_create(
                employee=request.user,
                defaults={
                    'template_data': template_data,
                    'is_active': True
                }
            )
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return render(request, 'attendance/register_fingerprint.html')
