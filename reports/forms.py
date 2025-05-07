from django import forms
from .models import ReportSchedule, ReportType

class ReportScheduleForm(forms.ModelForm):
    class Meta:
        model = ReportSchedule
        fields = ['report_type', 'email_recipients', 'schedule_time', 'is_active']
        widgets = {
            'report_type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select report type'
            }),
            'email_recipients': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter email addresses separated by commas'
            }),
            'schedule_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
    def clean_email_recipients(self):
        emails = self.cleaned_data['email_recipients']
        if emails:
            # Split by comma and clean each email
            email_list = [email.strip() for email in emails.split(',')]
            # Validate each email
            for email in email_list:
                if not forms.EmailField().clean(email):
                    raise forms.ValidationError(f'Invalid email address: {email}')
            return emails
        return emails 