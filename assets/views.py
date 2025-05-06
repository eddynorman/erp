import pandas as pd
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Q
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from .models import (
    Asset, AssetPurchase, DamagedAsset, DisposedAsset, AssetRepair,
    AssetLocation, AssetWarranty, AssetInsurance, MaintenanceSchedule,
    MaintenanceRecord, AssetDocument, AssetTransfer
)
from .forms import (
    AssetForm, AssetPurchaseForm, DamagedAssetForm, DisposedAssetForm,
    AssetFormSet, AssetRepairForm, AssetLocationForm, AssetWarrantyForm,
    AssetInsuranceForm, MaintenanceScheduleForm, MaintenanceRecordForm,
    AssetDocumentForm, AssetTransferForm
)

class AssetListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    permission_required = 'assets.can_view_assets'
    ordering = ["name"]
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        status = self.request.GET.get('status', '')
        department = self.request.GET.get('department', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(asset_tag__icontains=search_query) |
                Q(serial_number__icontains=search_query)
            )
        if category:
            queryset = queryset.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)
        if department:
            queryset = queryset.filter(department_id=department)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Asset.CATEGORY_CHOICES
        context['statuses'] = Asset.STATUS_CHOICES
        return context

class AssetDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"
    permission_required = 'assets.can_view_assets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = self.get_object()
        context.update({
            "purchases": AssetPurchase.objects.filter(asset=asset),
            "damaged": DamagedAsset.objects.filter(asset=asset),
            "disposed": DisposedAsset.objects.filter(asset=asset),
            "repaired": AssetRepair.objects.filter(asset=asset),
            "locations": AssetLocation.objects.filter(asset=asset),
            "warranties": AssetWarranty.objects.filter(asset=asset),
            "insurance_policies": AssetInsurance.objects.filter(asset=asset),
            "maintenance_schedules": MaintenanceSchedule.objects.filter(asset=asset),
            "maintenance_records": MaintenanceRecord.objects.filter(asset=asset),
            "documents": AssetDocument.objects.filter(asset=asset),
            "transfers": AssetTransfer.objects.filter(asset=asset),
        })
        return context

class AddAssetView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "assets/add_asset.html"
    form_class = AssetFormSet
    permission_required = 'assets.can_manage_assets'
    success_message = "Asset added successfully!"

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(self.request.POST or None, queryset=Asset.objects.none())

    def form_valid(self, form):
        formset = self.get_form()
        if formset.is_valid():
            formset.save()
            messages.success(self.request, "Assets added successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_list")

class EditAssetView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/edit_asset.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Asset updated successfully!"

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.object.pk})

class DeleteAssetView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Asset
    template_name = "assets/delete_asset.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Asset deleted successfully!"
    success_url = reverse_lazy("assets:asset_list")

class AddAssetPurchaseView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AssetPurchase
    form_class = AssetPurchaseForm
    template_name = "assets/add_purchase.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Purchase recorded successfully!"

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class EditPurchaseView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AssetPurchase
    form_class = AssetPurchaseForm
    template_name = "assets/edit_purchase.html"
    permission_required = 'assets.can_manage_assets'

    def form_valid(self, form):
        purchase = form.save()
        purchase.asset.update_totals2(purchase.quantity, purchase.price, purchase.purchase_date)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.object.asset.id})

class MarkDamagedView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = DamagedAsset
    form_class = DamagedAssetForm
    template_name = "assets/mark_damaged.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Asset marked as damaged."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class RepairAssetView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AssetRepair
    form_class = AssetRepairForm
    template_name = "assets/repair_asset.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Asset repaired successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class DisposeAssetView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = DisposedAsset
    form_class = DisposedAssetForm
    template_name = "assets/dispose_asset.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Asset disposed successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class AddLocationView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AssetLocation
    form_class = AssetLocationForm
    template_name = "assets/add_location.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Location added successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        form.instance.assigned_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class AddWarrantyView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AssetWarranty
    form_class = AssetWarrantyForm
    template_name = "assets/add_warranty.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Warranty added successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class AddInsuranceView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AssetInsurance
    form_class = AssetInsuranceForm
    template_name = "assets/add_insurance.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Insurance policy added successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class AddMaintenanceScheduleView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "assets/add_maintenance_schedule.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Maintenance schedule added successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class AddMaintenanceRecordView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = "assets/add_maintenance_record.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Maintenance record added successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        form.instance.performed_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class AddDocumentView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AssetDocument
    form_class = AssetDocumentForm
    template_name = "assets/add_document.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Document added successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class TransferAssetView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AssetTransfer
    form_class = AssetTransferForm
    template_name = "assets/transfer_asset.html"
    permission_required = 'assets.can_manage_assets'
    success_message = "Asset transferred successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['asset'] = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        return kwargs

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        form.instance.from_department = asset.department
        form.instance.from_user = asset.assigned_to
        form.instance.transferred_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class GeneratePDFReportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'assets.can_view_assets'

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="asset_report.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        data = [["Asset Name", "Department", "Category", "Current Value", "Usable Quantity", "Damaged", "Disposed"]]

        assets = Asset.objects.all()
        for asset in assets:
            asset.calculate_depreciation()  # Update current value
            data.append([
                asset.name,
                asset.department.department_name,
                asset.category,
                f"{asset.current_value:,.2f}",
                asset.available_quantity(),
                asset.quantity_damaged,
                asset.quantity_disposed,
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        doc.build(elements)
        return response

class GenerateExcelReportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'assets.can_view_assets'

    def get(self, request, *args, **kwargs):
        assets = Asset.objects.order_by("name")
        data = []

        for asset in assets:
            asset.calculate_depreciation()  # Update current value
            purchases = AssetPurchase.objects.filter(asset=asset)
            total_spent = sum(purchase.price for purchase in purchases)
            initial_purchase = purchases.order_by("purchase_date").first()
            initial_cost = initial_purchase.price if initial_purchase else 0
            bought = sum(purchase.quantity for purchase in purchases) - (initial_purchase.quantity if initial_purchase else 0)

            repairs = AssetRepair.objects.filter(asset=asset)
            total_repairs_cost = sum(repair.cost for repair in repairs)
            repaired = sum(repair.quantity for repair in repairs)
            latest_repair = repairs.order_by("date").first()
            latest_repair_date = latest_repair.date if latest_repair else None

            warranties = AssetWarranty.objects.filter(asset=asset, is_active=True)
            active_warranties = warranties.count()
            warranty_expiry = min([w.end_date for w in warranties]) if warranties else None

            insurance = AssetInsurance.objects.filter(asset=asset, is_active=True)
            active_insurance = insurance.count()
            insurance_expiry = min([i.end_date for i in insurance]) if insurance else None

            maintenance = MaintenanceSchedule.objects.filter(asset=asset, is_active=True)
            upcoming_maintenance = maintenance.filter(next_due__gte=timezone.now().date()).order_by('next_due').first()
            next_maintenance_date = upcoming_maintenance.next_due if upcoming_maintenance else None

            data.append([
                asset.name,
                asset.asset_tag,
                asset.department.department_name,
                asset.category,
                asset.asset_type,
                asset.condition,
                initial_purchase.quantity if initial_purchase else 0,
                asset.initial_purchase_date,
                f"{initial_cost:,.2f}",
                asset.latest_purchase_date,
                bought,
                f"{total_spent - initial_cost:,.2f}",
                f"{asset.current_value:,.2f}",
                latest_repair_date,
                repaired,
                f"{total_repairs_cost:,.2f}",
                asset.available_quantity(),
                asset.quantity_damaged,
                asset.quantity_disposed,
                active_warranties,
                warranty_expiry,
                active_insurance,
                insurance_expiry,
                next_maintenance_date,
                asset.get_maintenance_status(),
            ])

        df = pd.DataFrame(data, columns=[
            "Asset Name", "Asset Tag", "Department", "Category", "Type",
            "Condition", "Initial Quantity", "Initial Purchase Date", "Initial Cost",
            "Latest Purchase Date", "Additional Quantity", "Additional Cost",
            "Current Value", "Latest Repair Date", "Repaired Quantity", "Repair Cost",
            "Usable Quantity", "Damaged", "Disposed", "Active Warranties",
            "Warranty Expiry", "Active Insurance", "Insurance Expiry",
            "Next Maintenance", "Maintenance Status"
        ])

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="asset_report.xlsx"'

        with pd.ExcelWriter(response, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Assets")

        return response

@login_required
@permission_required('assets.can_view_assets')
def get_asset_details(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    asset.calculate_depreciation()
    
    data = {
        'name': asset.name,
        'asset_tag': asset.asset_tag,
        'current_value': float(asset.current_value),
        'available_quantity': asset.available_quantity(),
        'maintenance_status': asset.get_maintenance_status(),
        'is_maintenance_due': asset.is_maintenance_due(),
    }
    
    return JsonResponse(data)

@login_required
@permission_required('assets.can_view_assets')
def get_maintenance_due_assets(request):
    assets = Asset.objects.filter(
        Q(next_maintenance_date__lte=timezone.now().date()) |
        Q(status='under_maintenance')
    )
    
    data = [{
        'id': asset.id,
        'name': asset.name,
        'asset_tag': asset.asset_tag,
        'maintenance_status': asset.get_maintenance_status(),
        'department': asset.department.department_name,
    } for asset in assets]
    
    return JsonResponse({'assets': data})
