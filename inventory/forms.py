from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import *
from company.models import Branch,Department,Category
from django.core.exceptions import ValidationError
from django.utils import timezone

class StoreForm(forms.ModelForm):
    """Form for creating and editing stores."""
    
    class Meta:
        model = Store
        fields = ['name', 'address', 'branch', 'contact_person', 'contact_number', 'status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter store name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter store address'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'contact_person': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter any additional notes'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if Store.objects.filter(name=name).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('A store with this name already exists.')
        return name

class SalePointForm(forms.ModelForm):
    """Form for creating and editing sale points."""
    
    class Meta:
        model = SalePoint
        fields = ['name', 'address', 'branch', 'contact_person', 'contact_number', 'status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sale point name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sale point address'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'contact_person': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter any additional notes'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if SalePoint.objects.filter(name=name).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('A sale point with this name already exists.')
        return name

class SupplierForm(forms.ModelForm):
    """Form for creating and editing suppliers."""
    
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'contact_person', 'contact_number', 'email', 'status', 'payment_terms', 'tax_number', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter supplier name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter supplier address'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact person name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter payment terms'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tax number'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter any additional notes'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if Supplier.objects.filter(name=name).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('A supplier with this name already exists.')
        return name

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and Supplier.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('A supplier with this email already exists.')
        return email

class ItemForm(forms.ModelForm):
    """Form for creating and editing items."""
    
    class Meta:
        model = Item
        fields = [
            'name', 'bar_code', 'department', 'category', 'initial_stock',
            'status', 'buying_price', 'selling_price', 'smallest_unit',
            'is_sellable', 'is_service', 'minimum_stock', 'optimum_stock',
            'reorder_point', 'lead_time_days', 'location', 'weight',
            'dimensions', 'manufacturer', 'model_number', 'serial_number',
            'warranty_period', 'expiry_date', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'bar_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter barcode'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'initial_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'buying_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'smallest_unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter smallest unit'}),
            'is_sellable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_service': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'optimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'reorder_point': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'lead_time_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter storage location'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter dimensions (LxWxH)'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter manufacturer name'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter model number'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter serial number'}),
            'warranty_period': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter any additional notes'}),
        }

    def clean_bar_code(self):
        bar_code = self.cleaned_data['bar_code']
        if bar_code and Item.objects.filter(bar_code=bar_code).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('An item with this barcode already exists.')
        return bar_code

    def clean(self):
        cleaned_data = super().clean()
        buying_price = cleaned_data.get('buying_price')
        selling_price = cleaned_data.get('selling_price')
        minimum_stock = cleaned_data.get('minimum_stock')
        optimum_stock = cleaned_data.get('optimum_stock')
        reorder_point = cleaned_data.get('reorder_point')

        if buying_price and selling_price and selling_price < buying_price:
            raise ValidationError('Selling price cannot be less than buying price.')

        if minimum_stock and optimum_stock and optimum_stock < minimum_stock:
            raise ValidationError('Optimum stock cannot be less than minimum stock.')

        if minimum_stock and reorder_point and reorder_point > minimum_stock:
            raise ValidationError('Reorder point cannot be greater than minimum stock.')

        return cleaned_data

class ItemKitForm(forms.ModelForm):
    class Meta:
        model = ItemKit
        fields = ['name', 'department', 'category', 'selling_price']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        branch = Branch.objects.first()
        self.fields['department'].queryset = branch.department_set.all()
        self.fields['category'].queryset = Category.objects.none()

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['category'].queryset = Category.objects.filter(department=department_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['category'].queryset = Category.objects.filter(department=self.instance.department)

class ItemKitItemForm(forms.ModelForm):
    class Meta:
        model = ItemKitItem
        fields = ['item', 'quantity']

# Create an inline formset for managing items inside an Item Kit
ItemKitItemFormSet = inlineformset_factory(
    ItemKit, ItemKitItem, 
    form=ItemKitItemForm,
    extra=1,  # Allow adding extra items
    can_delete=True  # Allow deletion
)

class ItemUnitForm(forms.ModelForm):
    class Meta:
        model = ItemUnit
        fields = ['item', 'unit', 'smallest_units', 'buying_price', 'selling_price']
        
class AdjustmentForm(forms.ModelForm):
    """Form for creating inventory adjustments."""
    
    class Meta:
        model = Adjustment
        fields = ['item', 'quantity', 'reason', 'notes']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '-999999', 'max': '999999'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter adjustment details'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        item = cleaned_data.get('item')

        if item and quantity:
            if quantity < 0 and abs(quantity) > item.total_stock():
                raise ValidationError('Adjustment quantity cannot exceed available stock.')

        return cleaned_data

class RequisitionForm(forms.ModelForm):
    """Form for creating requisitions."""
    
    class Meta:
        model = Requisition
        fields = ['department', 'item', 'quantity', 'priority', 'notes']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter requisition details'}),
        }

class ReceivingForm(forms.ModelForm):
    """Form for recording received items."""
    
    class Meta:
        model = Receiving
        fields = ['supplier', 'reference_number', 'receiving_date', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter reference number'}),
            'receiving_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter receiving details'}),
        }

    def clean_receiving_date(self):
        receiving_date = self.cleaned_data['receiving_date']
        if receiving_date > timezone.now().date():
            raise ValidationError('Receiving date cannot be in the future.')
        return receiving_date

class IssueForm(forms.ModelForm):
    """Form for recording issued items."""
    
    class Meta:
        model = Issue
        fields = ['store', 'sale_point', 'item', 'quantity', 'notes']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'sale_point': forms.Select(attrs={'class': 'form-control'}),
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter issue details'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        store = cleaned_data.get('store')
        sale_point = cleaned_data.get('sale_point')
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')

        if not store and not sale_point:
            raise ValidationError('Either store or sale point must be specified.')

        if store and sale_point:
            raise ValidationError('Cannot specify both store and sale point.')

        if item and quantity:
            if store and quantity > item.store_stock:
                raise ValidationError('Issue quantity cannot exceed available store stock.')
            if sale_point and quantity > item.shop_stock:
                raise ValidationError('Issue quantity cannot exceed available shop stock.')

        return cleaned_data

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['transfer_type', 'from_store', 'to_store', 'from_salepoint', 'to_salepoint', 'user_responsible', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_store'].required = False
        self.fields['to_store'].required = False
        self.fields['from_salepoint'].required = False
        self.fields['to_salepoint'].required = False

        # Add JavaScript to dynamically show/hide fields based on transfer type
        self.fields['transfer_type'].widget.attrs.update({
            'onchange': 'handleTransferTypeChange(this.value)'
        })

class TransferItemForm(forms.ModelForm):
    class Meta:
        model = TransferItem
        fields = ['item', 'unit', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = ItemUnit.objects.all()

        if 'item' in self.data:
            try:
                item_id = int(self.data.get('item'))
                self.fields['unit'].queryset = ItemUnit.objects.filter(item_id=item_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.item:
            self.fields['unit'].queryset = ItemUnit.objects.filter(item=self.instance.item)

TransferItemFormSet = forms.inlineformset_factory(
    Transfer, TransferItem, form=TransferItemForm,
    extra=1, can_delete=True
)

class IssueItemForm(forms.ModelForm):
    class Meta:
        model = IssuedItem
        fields = ['item', 'unit', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = ItemUnit.objects.all()

        if 'item' in self.data:
            try:
                item_id = int(self.data.get('item'))
                self.fields['unit'].queryset = ItemUnit.objects.filter(item_id=item_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.item:
            self.fields['unit'].queryset = ItemUnit.objects.filter(item=self.instance.item)

IssueItemFormSet = forms.inlineformset_factory(
    Issue, IssuedItem, form=IssueItemForm,
    extra=1, can_delete=True
)

class IssueApprovalForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['approved_by', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
