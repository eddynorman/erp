"""
Sales Management Models

This module defines the data models for managing sales in the ERP system.

Key models include:
- Customer: Represents customers who make purchases
- Sale: Represents a sales transaction
- SaleItem: Individual items sold in a transaction
- SaleKit: Item kits sold in a transaction
- Payment: Records payments made for sales
- Return: Handles product returns
- ReturnItem: Individual items returned
- ReturnKit: Item kits returned
- Discount: Manages discounts applied to sales
- Tax: Handles tax calculations
- SalesPerson: Tracks sales performance by employee
"""

from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from inventory.models import Item, ItemKit, SalePoint
from company.models import Employee, Branch
from decimal import Decimal

class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    tax_number = models.CharField(max_length=50, blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def update_balance(self, amount):
        self.balance += amount
        self.save()

class Sale(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('credit', 'Credit'),
    )

    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    sale_point = models.ForeignKey(SalePoint, on_delete=models.PROTECT)
    sales_person = models.ForeignKey(Employee, on_delete=models.PROTECT)
    date = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale #{self.invoice_number} - {self.customer.name}"

    def calculate_totals(self):
        # Calculate subtotal from items and kits
        items_total = self.saleitem_set.aggregate(total=Sum('total_price'))['total'] or 0
        kits_total = self.salekit_set.aggregate(total=Sum('total_price'))['total'] or 0
        self.subtotal = items_total + kits_total

        # Calculate tax and discount
        self.tax_amount = self.subtotal * Decimal('0.16')  # 16% VAT
        self.discount_amount = self.subtotal * Decimal('0.00')  # Default discount

        # Calculate final total
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()

    def update_payment_status(self):
        total_paid = self.payment_set.aggregate(total=Sum('amount'))['total'] or 0
        if total_paid >= self.total_amount:
            self.payment_status = 'paid'
        elif total_paid > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'
        self.save()

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update sale totals
        self.sale.calculate_totals()

class SaleKit(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    kit = models.ForeignKey(ItemKit, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kit.name} - {self.quantity} units"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update sale totals
        self.sale.calculate_totals()

class Payment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Sale.PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Sale #{self.sale.invoice_number} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update sale payment status
        self.sale.update_payment_status()
        # Update customer balance if credit payment
        if self.payment_method == 'credit':
            self.sale.customer.update_balance(-self.amount)

class Return(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )

    sale = models.ForeignKey(Sale, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    return_number = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.TextField()
    approved_by = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True)
    completed_by = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True, related_name='returns_completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return #{self.return_number} - {self.customer.name}"

    def calculate_total(self):
        items_total = self.returnitem_set.aggregate(total=Sum('total_price'))['total'] or 0
        kits_total = self.returnkit_set.aggregate(total=Sum('total_price'))['total'] or 0
        self.total_amount = items_total + kits_total
        self.save()

    def approve(self, employee):
        self.status = 'approved'
        self.approved_by = employee
        self.save()

    def complete(self, employee):
        self.status = 'completed'
        self.completed_by = employee
        self.save()
        # Update customer balance
        self.customer.update_balance(self.total_amount)

class ReturnItem(models.Model):
    return_obj = models.ForeignKey(Return, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.return_obj.calculate_total()

class ReturnKit(models.Model):
    return_obj = models.ForeignKey(Return, on_delete=models.CASCADE)
    kit = models.ForeignKey(ItemKit, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kit.name} - {self.quantity} units"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.return_obj.calculate_total()

class Discount(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.percentage}%"

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.percentage}%"

class SalesPerson(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_returns = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.name} - {self.branch.name}"

    def update_stats(self):
        # Calculate total sales
        sales = Sale.objects.filter(sales_person=self.employee)
        self.total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0

        # Calculate total returns
        returns = Return.objects.filter(sale__sales_person=self.employee)
        self.total_returns = returns.aggregate(total=Sum('total_amount'))['total'] or 0

        # Calculate net sales
        self.net_sales = self.total_sales - self.total_returns
        self.save()
