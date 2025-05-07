from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Expense, ExpenseCategory, ExpenseType, RecurringExpense,
    ExpenseAttachment, ExpenseComment
)

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description', 'parent', 'budget', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'budget': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

class ExpenseTypeForm(forms.ModelForm):
    class Meta:
        model = ExpenseType
        fields = ['name', 'description', 'frequency', 'requires_approval', 
                 'approval_threshold', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'approval_threshold': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'title', 'description', 'amount', 'category', 'expense_type',
            'date', 'payment_method', 'receipt', 'reference_number',
            'department', 'tax_amount', 'additional_costs',
            'notes', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'additional_costs': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        expense_type = cleaned_data.get('expense_type')

        if expense_type and amount:
            if expense_type.requires_approval and amount > expense_type.approval_threshold:
                self.instance.status = 'submitted'
            else:
                self.instance.status = 'approved'

        return cleaned_data

class RecurringExpenseForm(forms.ModelForm):
    class Meta:
        model = RecurringExpense
        fields = [
            'title', 'description', 'amount', 'category', 'expense_type',
            'frequency', 'start_date', 'end_date', 'department'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be earlier than start date")

        return cleaned_data

class ExpenseAttachmentForm(forms.ModelForm):
    class Meta:
        model = ExpenseAttachment
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Brief description of the attachment'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Add file size validation (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 10MB")
            # Add file type validation
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif']
            if file.content_type not in allowed_types:
                raise ValidationError("Only PDF, JPEG, PNG, and GIF files are allowed")
        return file

class ExpenseCommentForm(forms.ModelForm):
    class Meta:
        model = ExpenseComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment here'}),
        }

class ExpenseFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.ModelChoiceField(queryset=ExpenseCategory.objects.all(), required=False)
    expense_type = forms.ModelChoiceField(queryset=ExpenseType.objects.all(), required=False)
    status = forms.ChoiceField(choices=[('', '----')] + Expense.STATUS_CHOICES, required=False)
    min_amount = forms.DecimalField(required=False, min_value=0)
    max_amount = forms.DecimalField(required=False, min_value=0)
    payment_method = forms.ChoiceField(
        choices=[('', '----')] + Expense.PAYMENT_METHOD_CHOICES,
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')

        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be earlier than start date")

        if min_amount and max_amount and max_amount < min_amount:
            raise ValidationError("Maximum amount cannot be less than minimum amount")

        return cleaned_data

class BulkExpenseActionForm(forms.Form):
    ACTION_CHOICES = [
        ('approve', 'Approve Selected'),
        ('reject', 'Reject Selected'),
        ('delete', 'Delete Selected'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    selected_expenses = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        expenses = kwargs.pop('expenses', None)
        super().__init__(*args, **kwargs)
        if expenses:
            self.fields['selected_expenses'].choices = [
                (expense.id, str(expense)) for expense in expenses
            ] 