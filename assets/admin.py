from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Asset, AssetPurchase, DamagedAsset, DisposedAsset, AssetRepair,
    AssetLocation, AssetWarranty, AssetInsurance, MaintenanceSchedule,
    MaintenanceRecord, AssetDocument, AssetTransfer
)

class AssetPurchaseInline(admin.TabularInline):
    model = AssetPurchase
    extra = 0
    fields = ['purchase_date', 'quantity', 'price', 'supplier']
    readonly_fields = ['purchase_date', 'quantity', 'price', 'supplier']

class DamagedAssetInline(admin.TabularInline):
    model = DamagedAsset
    extra = 0
    fields = ['quantity', 'reason', 'date']
    readonly_fields = ['quantity', 'reason', 'date']

class DisposedAssetInline(admin.TabularInline):
    model = DisposedAsset
    extra = 0
    fields = ['quantity', 'reason', 'date']
    readonly_fields = ['quantity', 'reason', 'date']

class AssetRepairInline(admin.TabularInline):
    model = AssetRepair
    extra = 0
    fields = ['quantity', 'description', 'date', 'cost']
    readonly_fields = ['quantity', 'description', 'date', 'cost']

class AssetLocationInline(admin.TabularInline):
    model = AssetLocation
    extra = 0
    fields = ['building', 'floor', 'room', 'shelf', 'date_assigned', 'assigned_by']
    readonly_fields = ['building', 'floor', 'room', 'shelf', 'date_assigned', 'assigned_by']

class AssetWarrantyInline(admin.TabularInline):
    model = AssetWarranty
    extra = 0
    fields = ['provider', 'warranty_number', 'start_date', 'end_date', 'is_active']
    readonly_fields = ['provider', 'warranty_number', 'start_date', 'end_date', 'is_active']

class AssetInsuranceInline(admin.TabularInline):
    model = AssetInsurance
    extra = 0
    fields = ['provider', 'policy_number', 'start_date', 'end_date', 'coverage_amount', 'is_active']
    readonly_fields = ['provider', 'policy_number', 'start_date', 'end_date', 'coverage_amount', 'is_active']

class MaintenanceScheduleInline(admin.TabularInline):
    model = MaintenanceSchedule
    extra = 0
    fields = ['maintenance_type', 'frequency', 'next_due', 'assigned_to', 'is_active']
    readonly_fields = ['maintenance_type', 'frequency', 'next_due', 'assigned_to', 'is_active']

class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = ['maintenance_type', 'start_date', 'end_date', 'status', 'performed_by', 'cost']
    readonly_fields = ['maintenance_type', 'start_date', 'end_date', 'status', 'performed_by', 'cost']

class AssetDocumentInline(admin.TabularInline):
    model = AssetDocument
    extra = 0
    fields = ['document_type', 'title', 'upload_date', 'uploaded_by', 'is_public']
    readonly_fields = ['document_type', 'title', 'upload_date', 'uploaded_by', 'is_public']

class AssetTransferInline(admin.TabularInline):
    model = AssetTransfer
    extra = 0
    fields = ['from_department', 'to_department', 'transfer_date', 'transferred_by']
    readonly_fields = ['from_department', 'to_department', 'transfer_date', 'transferred_by']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'asset_tag', 'category', 'department', 'asset_type',
        'condition', 'status', 'available_quantity', 'current_value',
        'maintenance_status'
    ]
    list_filter = [
        'category', 'asset_type', 'condition', 'status', 'department'
    ]
    search_fields = [
        'name', 'asset_tag', 'serial_number', 'model_number',
        'manufacturer', 'description'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'current_value', 'last_maintenance_date',
        'next_maintenance_date'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'asset_tag', 'category', 'department', 'asset_type',
                'condition', 'status', 'description'
            )
        }),
        ('Technical Details', {
            'fields': (
                'serial_number', 'model_number', 'manufacturer',
                'expected_lifespan', 'depreciation_rate'
            )
        }),
        ('Financial Information', {
            'fields': (
                'initial_purchase_date', 'latest_purchase_date',
                'purchase_cost', 'current_value'
            )
        }),
        ('Inventory', {
            'fields': (
                'quantity', 'quantity_damaged', 'quantity_disposed',
                'assigned_to', 'initial_supplier'
            )
        }),
        ('Maintenance', {
            'fields': (
                'last_maintenance_date', 'next_maintenance_date'
            )
        }),
        ('System Information', {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'notes'
            )
        }),
    )
    inlines = [
        AssetPurchaseInline, DamagedAssetInline, DisposedAssetInline,
        AssetRepairInline, AssetLocationInline, AssetWarrantyInline,
        AssetInsuranceInline, MaintenanceScheduleInline,
        MaintenanceRecordInline, AssetDocumentInline, AssetTransferInline
    ]

    def maintenance_status(self, obj):
        status = obj.get_maintenance_status()
        if 'Overdue' in status:
            return format_html('<span style="color: red;">{}</span>', status)
        elif 'Due in' in status and int(status.split()[2]) <= 7:
            return format_html('<span style="color: orange;">{}</span>', status)
        return status
    maintenance_status.short_description = 'Maintenance Status'

    def available_quantity(self, obj):
        return obj.available_quantity()
    available_quantity.short_description = 'Available Quantity'

@admin.register(AssetPurchase)
class AssetPurchaseAdmin(admin.ModelAdmin):
    list_display = ['asset', 'purchase_date', 'quantity', 'price', 'supplier']
    list_filter = ['purchase_date', 'supplier']
    search_fields = ['asset__name', 'supplier']
    date_hierarchy = 'purchase_date'

@admin.register(DamagedAsset)
class DamagedAssetAdmin(admin.ModelAdmin):
    list_display = ['asset', 'quantity', 'reason', 'date']
    list_filter = ['date']
    search_fields = ['asset__name', 'reason']
    date_hierarchy = 'date'

@admin.register(DisposedAsset)
class DisposedAssetAdmin(admin.ModelAdmin):
    list_display = ['asset', 'quantity', 'reason', 'date']
    list_filter = ['date']
    search_fields = ['asset__name', 'reason']
    date_hierarchy = 'date'

@admin.register(AssetRepair)
class AssetRepairAdmin(admin.ModelAdmin):
    list_display = ['asset', 'quantity', 'description', 'date', 'cost']
    list_filter = ['date']
    search_fields = ['asset__name', 'description']
    date_hierarchy = 'date'

@admin.register(AssetLocation)
class AssetLocationAdmin(admin.ModelAdmin):
    list_display = ['asset', 'building', 'floor', 'room', 'date_assigned', 'assigned_by']
    list_filter = ['building', 'floor', 'date_assigned']
    search_fields = ['asset__name', 'building', 'room']
    date_hierarchy = 'date_assigned'

@admin.register(AssetWarranty)
class AssetWarrantyAdmin(admin.ModelAdmin):
    list_display = ['asset', 'provider', 'warranty_number', 'start_date', 'end_date', 'is_active']
    list_filter = ['provider', 'is_active', 'start_date', 'end_date']
    search_fields = ['asset__name', 'provider', 'warranty_number']
    date_hierarchy = 'start_date'

@admin.register(AssetInsurance)
class AssetInsuranceAdmin(admin.ModelAdmin):
    list_display = ['asset', 'provider', 'policy_number', 'start_date', 'end_date', 'coverage_amount', 'is_active']
    list_filter = ['provider', 'is_active', 'start_date', 'end_date']
    search_fields = ['asset__name', 'provider', 'policy_number']
    date_hierarchy = 'start_date'

@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ['asset', 'maintenance_type', 'frequency', 'next_due', 'assigned_to', 'is_active']
    list_filter = ['maintenance_type', 'frequency', 'is_active', 'next_due']
    search_fields = ['asset__name', 'maintenance_type', 'description']
    date_hierarchy = 'next_due'

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ['asset', 'maintenance_type', 'start_date', 'end_date', 'status', 'performed_by', 'cost']
    list_filter = ['maintenance_type', 'status', 'start_date', 'end_date']
    search_fields = ['asset__name', 'maintenance_type', 'description', 'findings']
    date_hierarchy = 'start_date'

@admin.register(AssetDocument)
class AssetDocumentAdmin(admin.ModelAdmin):
    list_display = ['asset', 'document_type', 'title', 'upload_date', 'uploaded_by', 'is_public']
    list_filter = ['document_type', 'is_public', 'upload_date']
    search_fields = ['asset__name', 'title', 'description']
    date_hierarchy = 'upload_date'

@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = ['asset', 'from_department', 'to_department', 'transfer_date', 'transferred_by']
    list_filter = ['from_department', 'to_department', 'transfer_date']
    search_fields = ['asset__name', 'reason', 'notes']
    date_hierarchy = 'transfer_date'
