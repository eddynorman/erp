"""
Sales Management Forms

This module defines the forms for managing sales in the ERP system.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Customer, Sale, SaleItem, SaleKit, Payment, Return,
    ReturnItem, ReturnKit, Discount, Tax, SalesPerson
)
from inventory.models import Item, ItemKit, SalePoint
from company.models import Employee, Branch

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'tax_number', 'credit_limit', 'status']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise ValidationError('Phone number must contain only digits')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Customer.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('This email is already registered')
        return email

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'sale_point', 'sales_person', 'payment_method', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active customers
        self.fields['customer'].queryset = Customer.objects.filter(status='Active')
        # Filter only active sale points
        self.fields['sale_point'].queryset = SalePoint.objects.filter(status='Active')
        # Filter only active employees
        self.fields['sales_person'].queryset = Employee.objects.filter(status='Active')

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['item', 'quantity', 'unit_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only sellable items
        self.fields['item'].queryset = Item.objects.filter(is_sellable=True, status='Active')

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')

        if item and quantity:
            # Check if there's enough stock in the sale point
            sale_point = self.instance.sale.sale_point if self.instance.sale else None
            if sale_point:
                stock = item.salepointitem_set.filter(sale_point=sale_point).first()
                if not stock or stock.quantity < quantity:
                    raise ValidationError(f'Not enough stock available. Current stock: {stock.quantity if stock else 0}')

        return cleaned_data

class SaleKitForm(forms.ModelForm):
    class Meta:
        model = SaleKit
        fields = ['kit', 'quantity', 'unit_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active kits
        self.fields['kit'].queryset = ItemKit.objects.filter(status='Active')

    def clean(self):
        cleaned_data = super().clean()
        kit = cleaned_data.get('kit')
        quantity = cleaned_data.get('quantity')

        if kit and quantity:
            # Check if there's enough stock for all items in the kit
            sale_point = self.instance.sale.sale_point if self.instance.sale else None
            if sale_point:
                for kit_item in kit.itemkititem_set.all():
                    stock = kit_item.item.salepointitem_set.filter(sale_point=sale_point).first()
                    required_quantity = kit_item.quantity * quantity
                    if not stock or stock.quantity < required_quantity:
                        raise ValidationError(f'Not enough stock available for {kit_item.item.name}. Required: {required_quantity}, Available: {stock.quantity if stock else 0}')

        return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        sale = self.instance.sale if self.instance else None
        if sale:
            total_paid = sale.payment_set.exclude(pk=self.instance.pk if self.instance else None).aggregate(total=Sum('amount'))['total'] or 0
            remaining = sale.total_amount - total_paid
            if amount > remaining:
                raise ValidationError(f'Payment amount cannot exceed remaining balance of {remaining}')
        return amount

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['sale', 'customer', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only paid sales
        self.fields['sale'].queryset = Sale.objects.filter(payment_status='paid')

class ReturnItemForm(forms.ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['item', 'quantity', 'unit_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only items from the original sale
        if self.instance.return_obj:
            sale_items = self.instance.return_obj.sale.saleitem_set.values_list('item', flat=True)
            self.fields['item'].queryset = Item.objects.filter(pk__in=sale_items)

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')

        if item and quantity:
            # Check if the quantity doesn't exceed the original sale quantity
            return_obj = self.instance.return_obj
            if return_obj:
                original_quantity = return_obj.sale.saleitem_set.filter(item=item).first()
                if not original_quantity or quantity > original_quantity.quantity:
                    raise ValidationError(f'Return quantity cannot exceed original sale quantity of {original_quantity.quantity if original_quantity else 0}')

        return cleaned_data

class ReturnKitForm(forms.ModelForm):
    class Meta:
        model = ReturnKit
        fields = ['kit', 'quantity', 'unit_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only kits from the original sale
        if self.instance.return_obj:
            sale_kits = self.instance.return_obj.sale.salekit_set.values_list('kit', flat=True)
            self.fields['kit'].queryset = ItemKit.objects.filter(pk__in=sale_kits)

    def clean(self):
        cleaned_data = super().clean()
        kit = cleaned_data.get('kit')
        quantity = cleaned_data.get('quantity')

        if kit and quantity:
            # Check if the quantity doesn't exceed the original sale quantity
            return_obj = self.instance.return_obj
            if return_obj:
                original_quantity = return_obj.sale.salekit_set.filter(kit=kit).first()
                if not original_quantity or quantity > original_quantity.quantity:
                    raise ValidationError(f'Return quantity cannot exceed original sale quantity of {original_quantity.quantity if original_quantity else 0}')

        return cleaned_data

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['name', 'description', 'percentage', 'start_date', 'end_date', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise ValidationError('End date must be after start date')

        if start_date and start_date < timezone.now():
            raise ValidationError('Start date cannot be in the past')

        return cleaned_data

class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['name', 'percentage', 'is_active']

class SalesPersonForm(forms.ModelForm):
    class Meta:
        model = SalesPerson
        fields = ['employee', 'branch']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active employees
        self.fields['employee'].queryset = Employee.objects.filter(status='Active')
        # Filter only active branches
        self.fields['branch'].queryset = Branch.objects.filter(status='Active') 