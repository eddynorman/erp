# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, DetailView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
from company.models import Branch, Department, Category


class HomeView(View):
    def get(self, request):
        return render(request, 'inventory/index.html')
class StoreListView(ListView):
    model = Store
    template_name = 'store_list.html'
    context_object_name = 'stores'

class StoreCreateView(CreateView):
    model = Store
    form_class = StoreForm
    template_name = 'inventory/store_form.html'
    success_url = reverse_lazy('inventory/store_list')

class StoreUpdateView(UpdateView):
    model = Store
    form_class = StoreForm
    template_name = 'store_form.html'
    success_url = reverse_lazy('inventory/store_list')
class StoreDetailView(DetailView):
    model = Store
    context_object_name = 'store'
    template_name = 'inventory/store_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store_items'] = StoreItem.objects.filter(store=self.object)
        return context

class SalePointDetailView(DetailView):
    model = SalePoint
    template_name = 'inventory/salepoint_detail.html'
    context_object_name = "salepoint"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salepoint_items'] = SalePointItem.objects.filter(sale_point=self.object)
        return context

class StoreDeleteView(DeleteView):
    model = Store
    template_name = 'store_confirm_delete.html'
    success_url = reverse_lazy('inventory/store_list')

class SalePointCreateView(CreateView):
    model = SalePoint
    form_class = SalePointForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:salepoint_list')

class SalePointUpdateView(UpdateView):
    model = SalePoint
    form_class = SalePointForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:salepoint_list')

class SalePointListView(ListView):
    model = SalePoint
    template_name = 'inventory/salepoint_list.html'
    context_object_name = 'salepoints'

class SalePointDetailView(DetailView):
    model = SalePoint
    template_name = 'inventory/salepoint_detail.html'
    context_object_name = "salepoint"
    
class SalePointDeleteView(DeleteView):
    model = SalePoint
    template_name = 'inventory/gen_confirm_delete.html'
    success_url = reverse_lazy('inventory:salepoint_delete')
    

class SupplierListView(ListView):
    model = Supplier
    template_name = 'supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:supplier_list')
    
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:supplier_list')
    
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'inventory/gen_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')
    
class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/store_form.html'
    success_url = reverse_lazy('inventory:item_list')

class ItemListView(ListView):
    model = Item
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/store_form.html'
    success_url = reverse_lazy('inventory:item_list')

class ItemDeleteView(DeleteView):
    model = Item
    template_name = 'inventory/store_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_list')

class LoadCategories(View):
    def get(self, request):
        department_id = request.GET.get('department_id')
        categories = Category.objects.filter(department=department_id).values('id', 'category_name')
        return JsonResponse(list(categories), safe=False)


class ItemKitCreateView(CreateView):
    model = ItemKit
    form_class = ItemKitForm
    template_name = 'inventory/itemkit_form.html'
    success_url = reverse_lazy('inventory:itemkit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ItemKitItemFormSet(self.request.POST)
        else:
            context['formset'] = ItemKitItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object  # Link items to ItemKit
            formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ItemKitUpdateView(UpdateView):
    model = ItemKit
    form_class = ItemKitForm
    template_name = 'inventory/itemkit_form.html'
    success_url = reverse_lazy('inventory:itemkit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ItemKitItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ItemKitItemFormSet(instance=self.object)  # Ensure instance is set correctly
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()  # No need for commit=False unless you modify before saving
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)  # 🚀 Use this instead of redirect for consistency
        else:
            print("Formset errors:", formset.errors)
            return self.render_to_response(self.get_context_data(form=form))

class ItemKitListView(ListView):
    model = ItemKit
    template_name = 'inventory/itemkit_list.html'
    context_object_name = 'itemkits'

class ItemKitDetailView(DetailView):
    model = ItemKit
    template_name = 'inventory/itemkit_detail.html'

def deactivate_item_kit(request, pk):
    item_kit = get_object_or_404(ItemKit, pk=pk)
    item_kit.deactivate()
    return redirect('inventory:itemkit_list')

class ItemUnitCreateView(CreateView):
    model = ItemUnit
    form_class = ItemUnitForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:unit_list')

class ItemUnitUpdateView(UpdateView):
    model = ItemUnit
    form_class = ItemUnitForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:unit_list')

class ItemUnitListView(ListView):
    model = ItemUnit
    template_name = "inventory/units.html"
    context_object_name = 'units'

class ItemUnitDeleteView(DeleteView):
    model = ItemUnit
    template_name = 'inventory/gen_confirm_delete.html'
    success_url = reverse_lazy('inventory:unit_list')

class AdjustmentCreateView(CreateView):
    model = Adjustment
    form_class = AdjustmentForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:adjustment_list')
    
    def get_initial(self):
        initial = super().get_initial()
        item_id = self.kwargs.get('item_id')
        store_id = self.request.GET.get('store_id')
        sale_point_id = self.request.GET.get('sale_point_id')
        
        if item_id:
            initial['item'] = item_id
            
        if store_id:
            initial['store'] = store_id
            initial['in_store'] = True
            
        if sale_point_id:
            initial['sale_point'] = sale_point_id
            initial['in_store'] = False
            
        return initial
class AdjustmentListView(ListView):
    model = Adjustment
    template_name = 'inventory/adjustment_list.html'
    context_object_name = 'adjustments'

class RequisitionListView(ListView):
    model = Requisition
    template_name = 'inventory/requisition_list.html'
    context_object_name = 'requisitions'
    ordering = ['-date']

class RequisitionDetailView(DetailView):
    model = Requisition
    template_name = 'inventory/requisition_detail.html'
    context_object_name = 'requisition'
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["total_cost"] =sum
    #     return context
    

class RequisitionCreateView(CreateView):
    model = Requisition
    form_class = RequisitionForm
    template_name = 'inventory/requisition_form.html'
    success_url = reverse_lazy('inventory:requisition_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = RequisitionItemFormSet(self.request.POST)
        else:
            context['items_formset'] = RequisitionItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
            else:
                return self.form_invalid(form)
                
        messages.success(self.request, 'Requisition created successfully.')
        return super().form_valid(form)

class RequisitionUpdateView(UpdateView):
    model = Requisition
    form_class = RequisitionForm
    template_name = 'inventory/requisition_form.html'
    success_url = reverse_lazy('inventory:requisition_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = RequisitionItemFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['items_formset'] = RequisitionItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
            else:
                print("Formset errors:", items_formset.errors)
                print(items_formset)
                return self.form_invalid(form)
                
        messages.success(self.request, 'Requisition updated successfully.')
        return super().form_valid(form)

class RequisitionDeleteView(DeleteView):
    model = Requisition
    template_name = 'inventory/gen_confirm_delete.html'
    success_url = reverse_lazy('inventory:requisition_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Requisition deleted successfully.')
        return super().delete(request, *args, **kwargs)

class RequisitionApproveView(UpdateView):
    model = Requisition
    form_class = RequisitionApprovalForm
    template_name = 'inventory/requisition_approve.html'
    success_url = reverse_lazy('inventory:requisition_list')
    
    def form_valid(self, form):
        requisition = form.save(commit=False)
        if requisition.approved:
            requisition.approved_date = timezone.now()
        requisition.save()
        messages.success(self.request, 'Requisition approval status updated.')
        return super().form_valid(form)

# AJAX views for dynamic form handling
def get_item_details(request):
    item_id = request.GET.get('item_id')
    if item_id:
        item = get_object_or_404(Item, id=item_id)
        units = ItemUnit.objects.filter(item=item)
        
        # Return both unit data and their IDs
        return JsonResponse({
            'available_stock': item.total_stock(),
            'units': [{'id': unit.id, 'unit': str(unit.unit)} for unit in units]
        })
    return JsonResponse({'error': 'No item selected'})

def get_unit_price(request):
    unit_id = request.GET.get('unit_id')
    if not unit_id:
        return JsonResponse({'error': 'No unit selected'}, status=400)
    
    try:
        unit = ItemUnit.objects.get(id=unit_id)
        return JsonResponse({
            'buying_price': unit.buying_price,
        })
    except ItemUnit.DoesNotExist:
        return JsonResponse({'error': 'Unit not found'}, status=404)
    
class ReceivingCreateView(CreateView):
    model = Receiving
    form_class = ReceivingForm
    template_name = "inventory/receiving_form.html"
    success_url = reverse_lazy("inventory:receiving_list")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = ReceivedItemFormSet(self.request.POST)
        else:
            context["items_formset"] = ReceivedItemFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
           
            if items_formset.is_valid() and form.is_valid():
                self.object = form.save()
                items_formset.instance = self.object
                items_formset.save()
            else:
                return self.form_invalid(form)   
        messages.success(self.request,"Receiving Added Successfully!") 
        return super().form_valid(form)

class ReceivingUpdateView(UpdateView):
    model = Receiving
    form_class = ReceivingForm
    template_name = "inventory/receiving_form.html"
    success_url = reverse_lazy("inventory:receiving_list")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = ReceivedItemFormSet(self.request.POST, instance=self.object)
        else:
            context["items_formset"] = ReceivedItemFormSet(instance=self.object)
            
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            # Store the original received items before making changes
            original_receiving = self.get_object()
            original_items = list(original_receiving.receiveditem_set.all())
            
            # First, reverse the stock changes from the original items
            for original_item in original_items:
                qty = -1 * original_item.quantity * original_item.unit.smallest_units
                if original_receiving.is_store:
                    if original_receiving.store:
                        original_receiving.store.update_stock(qty, original_item.item)
                else:
                    if original_receiving.sale_point:
                        original_receiving.sale_point.update_stock(qty, original_item.item)
            
            # Now save the form and formset with new values
            if items_formset.is_valid():
                self.object = form.save()
                items_formset.instance = self.object
                items_formset.save()
                
                # The ReceivedItem.save() method will automatically update the stock
                # with the new quantities through its update_stock method
                
                messages.success(self.request, "Receiving Edited Successfully!")
                return super().form_valid(form)
            else:
                # Restore the original stock changes if formset is invalid
                for original_item in original_items:
                    qty = original_item.quantity * original_item.unit.smallest_units
                    if original_receiving.is_store:
                        if original_receiving.store:
                            original_receiving.store.update_stock(qty, original_item.item)
                    else:
                        if original_receiving.sale_point:
                            original_receiving.sale_point.update_stock(qty, original_item.item)
                
                return self.form_invalid(form)    
class ReceivingListView(ListView):
    model = Receiving
    context_object_name = "receivings"
    template_name = "inventory/receiving_list.html"
    ordering = ["-date"]

class ReceivingDetailView(DetailView):
    model = Receiving
    template_name = "inventory/receiving_detail.html"
    context_object_name = "receiving"


class ReceivingDeleteView(DeleteView):
    model = Receiving
    template_name = "inventory/gen_confirm_delete.html"
    success_url = reverse_lazy("inventory:receiving_list")
    
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Receiving deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
    
    # Add these functions to handle store item management
    def add_store_item(request, pk):
        store = get_object_or_404(Store, pk=pk)
        if request.method == 'POST':
            item_id = request.POST.get('item')
            quantity = int(request.POST.get('quantity', 0))
        
            if item_id and quantity > 0:
                item = get_object_or_404(Item, pk=item_id)
            
                # Check if item already exists in store
                store_item, created = StoreItem.objects.get_or_create(
                    store=store,
                    item=item,
                    defaults={'quantity': quantity}
                )
            
                if not created:
                    # Update existing item quantity
                    store_item.quantity += quantity
                    store_item.save()
                
                messages.success(request, f'Added {quantity} {item.name} to {store.name}')
            else:
                messages.error(request, 'Invalid item or quantity')
            
        return redirect('inventory:store_detail', pk=pk)

    def update_store_item(request, pk):
        store = get_object_or_404(Store, pk=pk)
        if request.method == 'POST':
            item_id = request.POST.get('item_id')
            quantity = int(request.POST.get('quantity', 0))
        
            if item_id:
                store_item = get_object_or_404(StoreItem, pk=item_id, store=store)
                store_item.quantity = quantity
                store_item.save()
            
                messages.success(request, f'Updated {store_item.item.name} quantity to {quantity}')
            else:
                messages.error(request, 'Invalid item')
            
        return redirect('inventory:store_detail', pk=pk)


# Add these functions to handle store item management
def add_store_item(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        item_id = request.POST.get('item')
        quantity = int(request.POST.get('quantity', 0))
        
        if item_id and quantity > 0:
            item = get_object_or_404(Item, pk=item_id)
            
            # Check if item already exists in store
            store_item, created = StoreItem.objects.get_or_create(
                store=store,
                item=item,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Update existing item quantity
                store_item.quantity += quantity
                store_item.save()
                
            messages.success(request, f'Added {quantity} {item.name} to {store.name}')
        else:
            messages.error(request, 'Invalid item or quantity')
            
    return redirect('inventory:store_detail', pk=pk)

def update_store_item(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 0))
        
        if item_id:
            store_item = get_object_or_404(StoreItem, pk=item_id, store=store)
            store_item.quantity = quantity
            store_item.save()
            
            messages.success(request, f'Updated {store_item.item.name} quantity to {quantity}')
        else:
            messages.error(request, 'Invalid item')
            
    return redirect('inventory:store_detail', pk=pk)



class TransferListView(ListView):
    model = Transfer
    template_name = 'inventory/transfer_list.html'
    context_object_name = 'transfers'
    ordering = ['-date']

class TransferCreateView(CreateView):
    model = Transfer
    form_class = TransferForm
    template_name = 'inventory/transfer_form.html'
    success_url = reverse_lazy('inventory:transfer_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = TransferItemFormSet(self.request.POST)
        else:
            context['items_formset'] = TransferItemFormSet()
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save(commit=False)
            
            # Validate based on transfer type
            transfer_type = form.cleaned_data['transfer_type']
            if transfer_type == 'store_to_store':
                if not form.cleaned_data['from_store'] or not form.cleaned_data['to_store']:
                    form.add_error(None, "Both source and destination stores are required for store-to-store transfers")
                    return self.form_invalid(form)
            elif transfer_type == 'salepoint_to_salepoint':
                if not form.cleaned_data['from_salepoint'] or not form.cleaned_data['to_salepoint']:
                    form.add_error(None, "Both source and destination sale points are required for sale point-to-sale point transfers")
                    return self.form_invalid(form)
            elif transfer_type == 'salepoint_to_store':
                if not form.cleaned_data['from_salepoint'] or not form.cleaned_data['to_store']:
                    form.add_error(None, "Both source sale point and destination store are required for sale point-to-store transfers")
                    return self.form_invalid(form)
            
            self.object.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
            else:
                return self.form_invalid(form)
                
        messages.success(self.request, 'Transfer created successfully.')
        return super().form_valid(form)

class TransferDetailView(DetailView):
    model = Transfer
    template_name = 'inventory/transfer_detail.html'
    context_object_name = 'transfer'

class TransferUpdateView(UpdateView):
    model = Transfer
    form_class = TransferForm
    template_name = 'inventory/transfer_form.html'
    success_url = reverse_lazy('inventory:transfer_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = TransferItemFormSet(self.request.POST, instance=self.object)
        else:
            context['items_formset'] = TransferItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        if self.object.completed:
            messages.error(self.request, "Cannot update a completed transfer.")
            return redirect('inventory:transfer_detail', pk=self.object.pk)
            
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save(commit=False)
            
            # Validate based on transfer type
            transfer_type = form.cleaned_data['transfer_type']
            if transfer_type == 'store_to_store':
                if not form.cleaned_data['from_store'] or not form.cleaned_data['to_store']:
                    form.add_error(None, "Both source and destination stores are required for store-to-store transfers")
                    return self.form_invalid(form)
            elif transfer_type == 'salepoint_to_salepoint':
                if not form.cleaned_data['from_salepoint'] or not form.cleaned_data['to_salepoint']:
                    form.add_error(None, "Both source and destination sale points are required for sale point-to-sale point transfers")
                    return self.form_invalid(form)
            elif transfer_type == 'salepoint_to_store':
                if not form.cleaned_data['from_salepoint'] or not form.cleaned_data['to_store']:
                    form.add_error(None, "Both source sale point and destination store are required for sale point-to-store transfers")
                    return self.form_invalid(form)
            
            self.object.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
            else:
                return self.form_invalid(form)
                
        messages.success(self.request, 'Transfer updated successfully.')
        return super().form_valid(form)

def complete_transfer(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk)
    
    if transfer.completed:
        messages.error(request, "This transfer is already completed.")
        return redirect('inventory:transfer_detail', pk=transfer.pk)
    
    try:
        transfer.complete_transfer()
        messages.success(request, "Transfer completed successfully.")
    except Exception as e:
        messages.error(request, f"Error completing transfer: {str(e)}")
    
    return redirect('inventory:transfer_detail', pk=transfer.pk)

# Issue Views
class IssueListView(ListView):
    model = Issue
    template_name = 'inventory/issue_list.html'
    context_object_name = 'issues'
    ordering = ['-date']

class IssueDetailView(DetailView):
    model = Issue
    template_name = 'inventory/issue_detail.html'
    context_object_name = 'issue'

class IssueCreateView(CreateView):
    model = Issue
    form_class = IssueForm
    template_name = 'inventory/issue_form.html'
    success_url = reverse_lazy('inventory:issue_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = IssueItemFormSet(self.request.POST)
        else:
            context['items_formset'] = IssueItemFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
            else:
                return self.form_invalid(form)
                
        messages.success(self.request, 'Issue request created successfully.')
        return super().form_valid(form)

class IssueUpdateView(UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = 'inventory/issue_form.html'
    success_url = reverse_lazy('inventory:issue_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = IssueItemFormSet(self.request.POST, instance=self.object)
        else:
            context['items_formset'] = IssueItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        if self.object.status != 'pending':
            messages.error(self.request, "Cannot update an issue that is not in pending status.")
            return redirect('inventory:issue_detail', pk=self.object.pk)
            
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
            else:
                return self.form_invalid(form)
                
        messages.success(self.request, 'Issue request updated successfully.')
        return super().form_valid(form)

class IssueApproveView(UpdateView):
    model = Issue
    form_class = IssueApprovalForm
    template_name = 'inventory/issue_approve.html'
    success_url = reverse_lazy('inventory:issue_list')
    
    def form_valid(self, form):
        issue = self.get_object()
        print(f"The Status {issue.status}")
        print(f"The user {self.object.approved_by}")
        if issue.status != 'pending':
            messages.error(self.request, "This issue request has already been processed.")
            return redirect('inventory:issue_detail', pk=self.object.pk)
            
        self.object = form.save()
        self.object.status = 'approved'
        issue.approve(self.object.approved_by)
        messages.success(self.request, 'Issue request status updated successfully.')
        return super().form_valid(form)


def complete_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if issue.status != 'approved':
        messages.error(request, "Only approved issue requests can be completed.")
        return redirect('inventory:issue_detail', pk=issue.pk)
    
    if issue.completed_date:
        messages.error(request, "This issue request has already been completed.")
        return redirect('inventory:issue_detail', pk=issue.pk)
    
    try:
        # Assuming the current user is an employee
        #employee = request.user.employee  # You might need to adjust this based on your user model
        employee = Employee.objects.first()
        issue.complete(employee)
        messages.success(request, "Issue request completed successfully.")
    except Exception as e:
        messages.error(request, f"Error completing issue request: {str(e)}")
    
    return redirect('inventory:issue_detail', pk=issue.pk)

def reject_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if issue.status != 'pending':
        messages.error(request, "Only pending issue requests can be rejected.")
        return redirect('inventory:issue_detail', pk=issue.pk)
    
    try:
        # Assuming the current user is an employee
        employee = request.user.employee  # You might need to adjust this based on your user model
        issue.reject(employee)
        messages.success(request, "Issue request rejected successfully.")
    except Exception as e:
        messages.error(request, f"Error rejecting issue request: {str(e)}")
    
    return redirect('inventory:issue_detail', pk=issue.pk)        