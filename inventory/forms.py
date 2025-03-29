# forms.py
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Store, Supplier, Item

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

# class ItemForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = ['name', 'description', 'unit_of_measurement', 'quantity']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.add_input(Submit('submit', 'Save'))
# Similar forms for Supplier, Item, Receiving, Issue, Recquisition