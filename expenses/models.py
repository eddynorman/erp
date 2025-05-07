from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_total_expenses(self, start_date=None, end_date=None):
        expenses = self.expenses.all()
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)
        return expenses.aggregate(total=models.Sum('amount'))['total'] or 0

class ExpenseType(models.Model):
    FREQUENCY_CHOICES = [
        ('one_time', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='one_time')
    requires_approval = models.BooleanField(default=False)
    approval_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('check', 'Check'),
        ('mobile_payment', 'Mobile Payment'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT, related_name='expenses')
    date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Receipt and documentation
    receipt = models.FileField(upload_to='expenses/receipts/%Y/%m/', blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # User tracking
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='expenses_created')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_approved')
    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_paid')
    
    # Department tracking
    department = models.ForeignKey('company.Department', on_delete=models.PROTECT, related_name='expenses')
    
    # Tax and additional costs
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    additional_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Timestamps and tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Notes and tags
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=200, blank=True)
    is_recurring = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date', '-created_at']
        permissions = [
            ("can_approve_expenses", "Can approve expenses"),
            ("can_reject_expenses", "Can reject expenses"),
            ("can_view_all_expenses", "Can view all expenses"),
        ]

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.date})"

    def get_total_amount(self):
        return self.amount + self.tax_amount + self.additional_costs

    def submit(self):
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()

    def approve(self, approved_by):
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def mark_as_paid(self, paid_by):
        self.status = 'paid'
        self.paid_by = paid_by
        self.paid_at = timezone.now()
        self.save()

class RecurringExpense(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField()
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    department = models.ForeignKey('company.Department', on_delete=models.PROTECT)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.frequency})"

    def generate_expense(self):
        """Generate a new expense instance from this recurring expense"""
        expense = Expense.objects.create(
            title=self.title,
            description=self.description,
            amount=self.amount,
            category=self.category,
            expense_type=self.expense_type,
            date=self.next_due_date,
            created_by=self.created_by,
            department=self.department,
            is_recurring=True
        )
        return expense

class ExpenseAttachment(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='expenses/attachments/%Y/%m/')
    description = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.expense}"

class ExpenseComment(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on {self.expense} by {self.user}"
