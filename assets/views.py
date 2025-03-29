import pandas as pd
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from .models import Asset, AssetPurchase, DamagedAsset, DisposedAsset, AssetRepair
from .forms import AssetForm, AssetPurchaseForm, DamagedAssetForm, DisposedAssetForm, AssetFormSet, AssetRepairForm


# List all assets
class AssetListView(ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    ordering = ["name"]

# Show asset details
class AssetDetailView(DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = self.get_object()
        context["purchases"] = AssetPurchase.objects.filter(asset=asset)
        context["damaged"] = DamagedAsset.objects.filter(asset=asset)
        context["disposed"] = DisposedAsset.objects.filter(asset=asset)
        context["repaired"] = AssetRepair.objects.filter(asset=asset)
        return context
    
class AddAssetView(SuccessMessageMixin, FormView):
    template_name = "assets/add_asset.html"
    form_class = AssetFormSet
    # success_url = reverse_lazy("assets:asset_list")
    # success_message = "Asset added successfully!"

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(self.request.POST or None, queryset=Asset.objects.none())

    def form_valid(self, form):
        formset = self.get_form()  # Get the formset instance
        
        if formset.is_valid():
            print("Formset is valid!")  # Debugging
            formset.save()
            messages.success(self.request, "Assets added successfully!")
        else:
            print("Formset errors:", formset.errors)  # Debugging

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_list")  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = self.get_form()
        return context

class AddAssetPurchaseView(SuccessMessageMixin, CreateView):
    model = AssetPurchase
    form_class = AssetPurchaseForm
    template_name = "assets/add_purchase.html"
    success_message = "Purchase recorded successfully!"

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class EditPurchaseView(SuccessMessageMixin, UpdateView):
    model = AssetPurchase
    form_class = AssetPurchaseForm
    template_name = "assets/edit_purchase.html"

    def form_valid(self, form):
        purchase = form.save()
        purchase.asset.update_totals2(purchase.quantity, purchase.price, purchase.purchase_date)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.object.asset.id})

class MarkDamagedView(SuccessMessageMixin, CreateView):
    model = DamagedAsset
    form_class = DamagedAssetForm
    template_name = "assets/mark_damaged.html"
    success_message = "Asset marked as damaged."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})


class RepairAssetView(SuccessMessageMixin, CreateView):
    model = AssetRepair
    form_class = AssetRepairForm
    template_name = "assets/repair_asset.html"
    success_message = "Asset repaired successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})


class DisposeAssetView(SuccessMessageMixin, CreateView):
    model = DisposedAsset
    form_class = DisposedAssetForm
    template_name = "assets/dispose_asset.html"
    success_message = "Asset disposed successfully."

    def form_valid(self, form):
        asset = get_object_or_404(Asset, id=self.kwargs["asset_id"])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.kwargs["asset_id"]})

class GeneratePDFReportView(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="asset_report.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        data = [["Asset Name", "Department", "Category", "Current Value", "Usable Quantity", "Damaged", "Disposed"]]

        assets = Asset.objects.all()
        for asset in assets:
            purchases = AssetPurchase.objects.filter(asset=asset)
            total_spent = sum(purchase.price for purchase in purchases)

            data.append([
                asset.name,
                asset.department.department_name,
                asset.category,
                f"{total_spent:,.2f}",
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


class GenerateExcelReportView(View):
    def get(self, request, *args, **kwargs):
        assets = Asset.objects.order_by("name")
        data = []

        for asset in assets:
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

            data.append([
                asset.name,
                asset.department.department_name,
                asset.category,
                initial_purchase.quantity if initial_purchase else 0,
                asset.initial_purchase_date,
                f"{initial_cost:,.2f}",
                asset.latest_purchase_date,
                bought,
                f"{total_spent - initial_cost:,.2f}",
                latest_repair_date,
                repaired,
                total_repairs_cost,
                asset.available_quantity(),
                asset.quantity_damaged,
                asset.quantity_disposed,
            ])

        df = pd.DataFrame(data, columns=[
            "Asset Name", "Department", "Category",
            "Initial Quantity", "Initial Purchase Date", "Initial Cost",
            "New Purchase Date", "Quantity", "Total Spent",
            "Repair Date", "Quantity", "Repairs Cost",
            "Usable Quantity", "Damaged", "Disposed",
        ])

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="asset_report.xlsx"'

        with pd.ExcelWriter(response, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Assets")

        return response
