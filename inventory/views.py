# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, DetailView
from django.http import JsonResponse
from django.urls import reverse_lazy
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

class StoreDeleteView(DeleteView):
    model = Store
    template_name = 'store_confirm_delete.html'
    success_url = reverse_lazy('inventory/store_list')

class SupplierListView(ListView):
    model = Supplier
    template_name = 'supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('supplier_list')
    
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('supplier_list')
    
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')
    
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

class ItemOtherUnitCreateView(CreateView):
    model = ItemOtherUnit
    form_class = ItemOtherUnitForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:other_unit_list')

class ItemOtherUnitUpdateView(UpdateView):
    model = ItemOtherUnit
    form_class = ItemOtherUnitForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:other_unit_list')

class ItemOtherUnitListView(ListView):
    model = ItemOtherUnit
    template_name = "inventory/other_units.html"
    context_object_name = 'units'

class ItemOtherUnitDeleteView(DeleteView):
    model = ItemOtherUnit
    template_name = 'inventory/gen_confirm_delete.html'
    success_url = reverse_lazy('inventory:other_unit_list')

class AdjustmentCreateView(CreateView):
    model = Adjustment
    form_class = AdjustmentForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:adjustment_list')

class AdjustmentListView(ListView):
    model = Adjustment
    template_name = 'inventory/adjustment_list.html'
    context_object_name = 'adjustments'

