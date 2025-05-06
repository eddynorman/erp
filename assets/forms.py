from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Asset, AssetPurchase, DamagedAsset, DisposedAsset, AssetRepair,
    AssetLocation, AssetWarranty, AssetInsurance, MaintenanceSchedule,
    MaintenanceRecord, AssetDocument, AssetTransfer
)

class CustomDateInput(forms.DateInput):
    input_type = 'date'

class AssetForm(ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'asset_tag', 'category', 'department', 'asset_type',
            'condition', 'initial_purchase_date', 'purchase_cost', 'quantity',
            'assigned_to', 'status', 'initial_supplier', 'description',
            'serial_number', 'model_number', 'manufacturer', 'expected_lifespan',
            'depreciation_rate', 'notes'
        ]
        widgets = {
            'initial_purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_asset_tag(self):
        asset_tag = self.cleaned_data['asset_tag']
        if Asset.objects.filter(asset_tag=asset_tag).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError("This asset tag is already in use.")
        return asset_tag

    def clean_initial_purchase_date(self):
        date = self.cleaned_data['initial_purchase_date']
        if date > timezone.now().date():
            raise ValidationError("Purchase date cannot be in the future.")
        return date

    def clean_depreciation_rate(self):
        rate = self.cleaned_data['depreciation_rate']
        if rate < 0 or rate > 100:
            raise ValidationError("Depreciation rate must be between 0 and 100.")
        return rate

class AssetPurchaseForm(ModelForm):
    class Meta:
        model = AssetPurchase
        fields = ['purchase_date', 'quantity', 'price', 'supplier']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_purchase_date(self):
        date = self.cleaned_data['purchase_date']
        if date > timezone.now().date():
            raise ValidationError("Purchase date cannot be in the future.")
        return date

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")
        return quantity

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price

class DamagedAssetForm(ModelForm):
    class Meta:
        model = DamagedAsset
        fields = ['quantity', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        asset = self.instance.asset if self.instance else None
        if asset and quantity > asset.available_quantity():
            raise ValidationError(f"Quantity cannot exceed available quantity ({asset.available_quantity()}).")
        return quantity

class DisposedAssetForm(ModelForm):
    class Meta:
        model = DisposedAsset
        fields = ['quantity', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        asset = self.instance.asset if self.instance else None
        if asset and quantity > asset.quantity_damaged:
            raise ValidationError(f"Quantity cannot exceed damaged quantity ({asset.quantity_damaged}).")
        return quantity

class AssetRepairForm(ModelForm):
    class Meta:
        model = AssetRepair
        fields = ['quantity', 'description', 'date', 'cost']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        asset = self.instance.asset if self.instance else None
        if asset and quantity > asset.quantity_damaged:
            raise ValidationError(f"Quantity cannot exceed damaged quantity ({asset.quantity_damaged}).")
        return quantity

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise ValidationError("Repair date cannot be in the future.")
        return date

class AssetLocationForm(ModelForm):
    class Meta:
        model = AssetLocation
        fields = ['building', 'floor', 'room', 'shelf', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class AssetWarrantyForm(ModelForm):
    class Meta:
        model = AssetWarranty
        fields = ['provider', 'start_date', 'end_date', 'coverage_details', 'warranty_number', 'is_active', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'coverage_details': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise ValidationError("End date must be after start date.")

        return cleaned_data

class AssetInsuranceForm(ModelForm):
    class Meta:
        model = AssetInsurance
        fields = [
            'provider', 'policy_number', 'start_date', 'end_date',
            'coverage_amount', 'premium_amount', 'coverage_details',
            'is_active', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'coverage_details': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        coverage_amount = cleaned_data.get('coverage_amount')
        premium_amount = cleaned_data.get('premium_amount')

        if start_date and end_date and start_date >= end_date:
            raise ValidationError("End date must be after start date.")

        if coverage_amount and coverage_amount <= 0:
            raise ValidationError("Coverage amount must be greater than 0.")

        if premium_amount and premium_amount <= 0:
            raise ValidationError("Premium amount must be greater than 0.")

        return cleaned_data

class MaintenanceScheduleForm(ModelForm):
    class Meta:
        model = MaintenanceSchedule
        fields = [
            'maintenance_type', 'frequency', 'next_due',
            'assigned_to', 'estimated_cost', 'description', 'is_active'
        ]
        widgets = {
            'next_due': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_next_due(self):
        next_due = self.cleaned_data['next_due']
        if next_due < timezone.now().date():
            raise ValidationError("Next due date cannot be in the past.")
        return next_due

    def clean_estimated_cost(self):
        cost = self.cleaned_data['estimated_cost']
        if cost < 0:
            raise ValidationError("Estimated cost cannot be negative.")
        return cost

class MaintenanceRecordForm(ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'maintenance_type', 'start_date', 'end_date', 'status',
            'performed_by', 'cost', 'description', 'findings',
            'recommendations', 'parts_replaced'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'findings': forms.Textarea(attrs={'rows': 3}),
            'recommendations': forms.Textarea(attrs={'rows': 3}),
            'parts_replaced': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        status = cleaned_data.get('status')

        if start_date and end_date and start_date >= end_date:
            raise ValidationError("End date must be after start date.")

        if status == 'completed' and not end_date:
            raise ValidationError("End date is required for completed maintenance.")

        return cleaned_data

class AssetDocumentForm(ModelForm):
    class Meta:
        model = AssetDocument
        fields = ['document_type', 'title', 'file', 'description', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError("File size must be no more than 10MB.")
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword',
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if file.content_type not in allowed_types:
                raise ValidationError("File type not supported. Please upload PDF, JPEG, PNG, or Word documents.")
        return file

class AssetTransferForm(ModelForm):
    class Meta:
        model = AssetTransfer
        fields = ['to_department', 'to_user', 'reason', 'notes']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.asset = kwargs.pop('asset', None)
        super().__init__(*args, **kwargs)
        if self.asset:
            self.fields['to_department'].queryset = Department.objects.exclude(id=self.asset.department.id)

    def clean_to_department(self):
        to_department = self.cleaned_data['to_department']
        if self.asset and to_department == self.asset.department:
            raise ValidationError("Asset must be transferred to a different department.")
        return to_department

# Formset for bulk asset creation
AssetFormSet = inlineformset_factory(
    Asset,
    AssetPurchase,
    form=AssetPurchaseForm,
    extra=1,
    can_delete=True
)
