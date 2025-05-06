# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, DetailView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, F, Q

from .models import *
from .forms import *
from company.models import Branch, Department, Category


class HomeView(View):
    def get(self, request):
        return render(request, 'inventory/index.html')

@login_required
def store_list(request):
    """View for listing all stores with search and filter functionality."""
    stores = Store.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        stores = stores.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(contact_person__name__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        stores = stores.filter(status=status)
    
    # Pagination
    paginator = Paginator(stores, 10)
    page_number = request.GET.get('page')
    stores = paginator.get_page(page_number)
    
    context = {
        'stores': stores,
        'status_choices': Store.STATUS_CHOICES,
    }
    return render(request, 'inventory/store_list.html', context)

@login_required
def store_create(request):
    """View for creating a new store."""
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save()
            messages.success(request, f'Store "{store.name}" created successfully.')
            return redirect('store_detail', pk=store.pk)
    else:
        form = StoreForm()
    
    return render(request, 'inventory/store_form.html', {'form': form, 'action': 'Create'})

@login_required
def store_edit(request, pk):
    """View for editing an existing store."""
    store = get_object_or_404(Store, pk=pk)
    
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            store = form.save()
            messages.success(request, f'Store "{store.name}" updated successfully.')
            return redirect('store_detail', pk=store.pk)
    else:
        form = StoreForm(instance=store)
    
    return render(request, 'inventory/store_form.html', {
        'form': form,
        'store': store,
        'action': 'Edit'
    })

@login_required
def store_detail(request, pk):
    """View for displaying store details and inventory."""
    store = get_object_or_404(Store, pk=pk)
    items = store.storeitem_set.select_related('item').all()
    
    # Calculate total value
    total_value = sum(item.quantity * item.item.buying_price for item in items)
    
    context = {
        'store': store,
        'items': items,
        'total_value': total_value,
    }
    return render(request, 'inventory/store_detail.html', context)

@login_required
def item_list(request):
    """View for listing all items with search and filter functionality."""
    items = Item.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(bar_code__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        items = items.filter(status=status)
    
    # Filter by department
    department = request.GET.get('department', '')
    if department:
        items = items.filter(department_id=department)
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        items = items.filter(category_id=category)
    
    # Filter by stock level
    stock_level = request.GET.get('stock_level', '')
    if stock_level == 'low':
        items = items.filter(store_stock__lte=F('minimum_stock'))
    elif stock_level == 'out':
        items = items.filter(store_stock=0)
    
    # Pagination
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    items = paginator.get_page(page_number)
    
    context = {
        'items': items,
        'status_choices': Item.STATUS_CHOICES,
    }
    return render(request, 'inventory/item_list.html', context)

@login_required
def item_create(request):
    """View for creating a new item."""
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                item = form.save()
                messages.success(request, f'Item "{item.name}" created successfully.')
                return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm()
    
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Create'})

@login_required
def item_edit(request, pk):
    """View for editing an existing item."""
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Item "{item.name}" updated successfully.')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'inventory/item_form.html', {
        'form': form,
        'item': item,
        'action': 'Edit'
    })

@login_required
def item_detail(request, pk):
    """View for displaying item details and stock information."""
    item = get_object_or_404(Item, pk=pk)
    
    # Get stock information
    store_items = item.storeitem_set.select_related('store').all()
    sale_point_items = item.salepointitem_set.select_related('sale_point').all()
    
    # Get recent transactions
    recent_adjustments = item.adjustment_set.order_by('-date')[:5]
    recent_issues = item.issue_set.order_by('-date')[:5]
    recent_receivings = item.receiving_set.order_by('-date')[:5]
    
    context = {
        'item': item,
        'store_items': store_items,
        'sale_point_items': sale_point_items,
        'recent_adjustments': recent_adjustments,
        'recent_issues': recent_issues,
        'recent_receivings': recent_receivings,
    }
    return render(request, 'inventory/item_detail.html', context)

@login_required
def adjustment_create(request):
    """View for creating a new inventory adjustment."""
    if request.method == 'POST':
        form = AdjustmentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                adjustment = form.save(commit=False)
                adjustment.user_responsible = request.user
                adjustment.save()
                
                # Update stock
                item = adjustment.item
                if adjustment.quantity > 0:
                    item.store_stock += adjustment.quantity
                else:
                    item.store_stock += adjustment.quantity
                item.save()
                
                messages.success(request, 'Inventory adjustment created successfully.')
                return redirect('item_detail', pk=item.pk)
    else:
        form = AdjustmentForm()
    
    return render(request, 'inventory/adjustment_form.html', {'form': form})

@login_required
def requisition_create(request):
    """View for creating a new requisition."""
    if request.method == 'POST':
        form = RequisitionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                requisition = form.save(commit=False)
                requisition.user_responsible = request.user
                requisition.save()
                
                messages.success(request, 'Requisition created successfully.')
                return redirect('requisition_detail', pk=requisition.pk)
    else:
        form = RequisitionForm()
    
    return render(request, 'inventory/requisition_form.html', {'form': form})

@login_required
def receiving_create(request):
    """View for creating a new receiving record."""
    if request.method == 'POST':
        form = ReceivingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                receiving = form.save(commit=False)
                receiving.user_responsible = request.user
                receiving.save()
                
                messages.success(request, 'Receiving record created successfully.')
                return redirect('receiving_detail', pk=receiving.pk)
    else:
        form = ReceivingForm()
    
    return render(request, 'inventory/receiving_form.html', {'form': form})

@login_required
def issue_create(request):
    """View for creating a new issue record."""
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                issue = form.save(commit=False)
                issue.user_responsible = request.user
                issue.save()
                
                # Update stock
                item = issue.item
                if issue.store:
                    item.store_stock -= issue.quantity
                else:
                    item.shop_stock -= issue.quantity
                item.save()
                
                messages.success(request, 'Issue record created successfully.')
                return redirect('issue_detail', pk=issue.pk)
    else:
        form = IssueForm()
    
    return render(request, 'inventory/issue_form.html', {'form': form})

@login_required
def get_item_stock(request, item_id):
    """API endpoint for getting item stock information."""
    try:
        item = Item.objects.get(pk=item_id)
        data = {
            'store_stock': item.store_stock,
            'shop_stock': item.shop_stock,
            'total_stock': item.total_stock(),
            'minimum_stock': item.minimum_stock,
            'optimum_stock': item.optimum_stock,
            'needs_reorder': item.needs_reorder(),
        }
        return JsonResponse(data)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)

@login_required
def get_low_stock_items(request):
    """API endpoint for getting items that need reordering."""
    items = Item.objects.filter(store_stock__lte=F('minimum_stock'))
    data = [{
        'id': item.id,
        'name': item.name,
        'current_stock': item.store_stock,
        'minimum_stock': item.minimum_stock,
        'optimum_stock': item.optimum_stock,
    } for item in items]
    return JsonResponse({'items': data})

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