from django.core.management.base import BaseCommand
from django.utils import timezone
from reports.models import ReportSchedule, ReportHistory
from django.core.mail import send_mail
from django.conf import settings
import os
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class Command(BaseCommand):
    help = 'Generates scheduled reports and sends them via email'

    def handle(self, *args, **options):
        current_time = timezone.now().time()
        schedules = ReportSchedule.objects.filter(
            is_active=True,
            schedule_time__hour=current_time.hour,
            schedule_time__minute=current_time.minute
        )

        for schedule in schedules:
            try:
                # Generate report
                report_type = schedule.report_type
                if report_type.name == 'Sales Report':
                    data = self.generate_sales_report()
                elif report_type.name == 'Inventory Report':
                    data = self.generate_inventory_report()
                else:
                    continue

                # Create report files
                report_files = []
                if report_type.default_format in ['pdf', 'both']:
                    pdf_file = self.generate_pdf_report(data, report_type.name)
                    report_files.append(('pdf', pdf_file))
                
                if report_type.default_format in ['excel', 'both']:
                    excel_file = self.generate_excel_report(data, report_type.name)
                    report_files.append(('excel', excel_file))

                # Save report history
                report_history = ReportHistory.objects.create(
                    report_type=report_type,
                    user=schedule.user,
                    schedule=schedule,
                    file_path=f"reports/{report_type.name}_{timezone.now().strftime('%Y%m%d')}",
                    format=report_type.default_format,
                    status='success'
                )

                # Send email with attachments
                subject = f"Scheduled Report: {report_type.name}"
                message = f"Please find attached the {report_type.name} as requested."
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email.strip() for email in schedule.email_recipients.split(',')]

                # Send email with attachments
                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=False,
                    attachments=[(f"{report_type.name}.{fmt}", file, f"application/{fmt}") 
                               for fmt, file in report_files]
                )

                # Update schedule
                schedule.last_run = timezone.now()
                schedule.save()

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully generated and sent {report_type.name}')
                )

            except Exception as e:
                ReportHistory.objects.create(
                    report_type=schedule.report_type,
                    user=schedule.user,
                    schedule=schedule,
                    status='failed',
                    error_message=str(e)
                )
                self.stdout.write(
                    self.style.ERROR(f'Failed to generate {schedule.report_type.name}: {str(e)}')
                )

    def generate_sales_report(self):
        # Implement actual sales report generation logic
        return pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Sales': [1000, 1500],
            'Products': ['Product A', 'Product B']
        })

    def generate_inventory_report(self):
        # Implement actual inventory report generation logic
        return pd.DataFrame({
            'Product': ['Product A', 'Product B'],
            'Quantity': [100, 200],
            'Value': [1000, 2000]
        })

    def generate_pdf_report(self, data, report_name):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add report title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, report_name)
        
        # Add report data
        p.setFont("Helvetica", 12)
        y = 700
        for index, row in data.iterrows():
            for col in data.columns:
                p.drawString(100, y, f"{col}: {row[col]}")
                y -= 20
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    def generate_excel_report(self, data, report_name):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            data.to_excel(writer, sheet_name='Report', index=False)
        buffer.seek(0)
        return buffer 