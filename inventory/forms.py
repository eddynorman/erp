# forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Store, Supplier, Item, StoreItem
from company.models import Branch,Department,Category

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address', 'contact_person', 'contact_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'contact_person', 'contact_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))

class ItemForm(forms.ModelForm):
    store = forms.ModelChoiceField(queryset=Store.objects.all(), required=True, help_text="Select a store for this item")
    class Meta:
        model = Item
        fields = ['name', 'bar_code','department','category','initial_stock','buying_price','selling_price','is_sellable','smallest_unit','minimum_stock','optimum_stock']
        
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

    def save(self, commit=True):
        item = super().save(commit=False)
        if commit:
            item.save()
            store = self.cleaned_data['store']
            quantity = item.initial_stock
            StoreItem.objects.create(store=store, item=item, quantity=quantity) 
            
        return item
# Similar forms for Supplier, Item, Receiving, Issue, Recquisition