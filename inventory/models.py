"""
Inventory Management Models

This module defines the data models for managing inventory in a retail/production environment.

Key models include:
- Store: Represents storage locations for items not in shop/production areas
- SalePoint: Represents retail/sales locations
- Supplier: Represents vendors who supply inventory items
- Item: Core inventory item with stock tracking across locations
- StoreItem: Tracks item quantities in specific stores
- SalePointItem: Tracks item quantities at specific sale points
- ItemUnit: Defines units of measurement for items
- ItemKit: Represents bundled items sold together
- Adjustment: Records inventory adjustments with reasons
- Requisition: Tracks requests for items from departments
- Receiving: Records items received from suppliers
- Issue: Manages movement of items between stores and shops

These models support inventory operations including stock tracking, transfers,
requisitions, and adjustments across multiple locations.
"""

from django.db import models,transaction
from django.db.models import F
from company.models import Department, Category, Employee, Branch
from django.utils import timezone

# Store for storing items not in the shop/production areas
class Store(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    branch = models.ForeignKey(Branch,on_delete=models.CASCADE)
    contact_person = models.ForeignKey(Employee, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default="Active")

    def __str__(self):
        return self.name
    
    def update_stock(self, qty, item):
        print(f"Updating stock for {item.name} in {self.name} by {qty}")
        if self.storeitem_set.filter(item=item):
            self.storeitem_set.filter(item=item).update(quantity=F('quantity') + qty)
            print(f"Updated stock for {item.name} in {self.name} by {qty}")
            item.calculate_store_stock()
            print(f"called calculate {item.name} in {self.name} by {qty}")
        else:
            StoreItem.objects.create(store=self, item=item, quantity=qty)
        self.save()

class SalePoint(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    branch = models.ForeignKey(Branch,on_delete=models.CASCADE)
    contact_person = models.ForeignKey(Employee, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default="Active")

    def __str__(self):
        return self.name
    
    def update_stock(self, qty, item):
        print(f"Updating stock for {item.name} in {self.name} by {qty}")
        if self.salepointitem_set.filter(item=item):
            self.salepointitem_set.filter(item=item).update(quantity=F('quantity') + qty)
            print(f"Updated stock for {item.name} in {self.name} by {qty}")
            item.calculate_shop_stock()
            print(f"called calculate {item.name} in {self.name} by {qty}")
        else:
            SalePointItem.objects.create(sale_point=self, item=item, quantity=qty)
        self.save()
class Supplier(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default="Active")

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=200)
    bar_code = models.CharField(max_length=20, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    initial_stock = models.IntegerField(default=0)
    store_stock = models.IntegerField(default=0)
    shop_stock = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="Active")
    buying_price = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    smallest_unit = models.CharField(max_length=20)   
    is_sellable = models.BooleanField(default=True)
    is_service = models.BooleanField(default=False)
    minimum_stock = models.IntegerField(default=0)
    optimum_stock = models.IntegerField(default=0)

    def calculate_store_stock(self):
        """Calculate store stock based on StoreItem objects and adjust store stock."""
        print("Calculating store stock...")
        self.store_stock = sum(store_item.quantity for store_item in self.storeitem_set.all())
        self.save()
    
    def calculate_shop_stock(self):
        """Calculate shop stock based on ShopItem objects and adjust shop stock."""
        self.shop_stock = sum(shop_item.quantity for shop_item in self.salepointitem_set.all())
        self.save()
    
    def total_stock(self):
        return self.store_stock + self.shop_stock

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.store_stock = self.initial_stock
            self.shop_stock = 0
            ItemUnit.objects.create(item=self, unit=self.smallest_unit, smallest_units=1, buying_price=self.buying_price, selling_price=self.selling_price)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"

class StoreItem(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'item')  # Ensures an item can't be duplicated in the same store

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(f"Saving StoreItem for {self.item.name} in {self.store.name} with quantity {self.quantity}")
        self.item.calculate_store_stock()
    
    def __str__(self):
        return f"{self.item.name} - {self.store.name}: {self.quantity}"

class SalePointItem(models.Model):
    sale_point = models.ForeignKey(SalePoint, on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('sale_point', 'item')  # Ensures an item can't be duplicated in the same store

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(f"Saving StoreItem for {self.item.name} in {self.sale_point.name} with quantity {self.quantity}")
        self.item.calculate_shop_stock()
    
    def __str__(self):
        return f"{self.item.name} - {self.sale_point.name}: {self.quantity}"

class ItemUnit(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    unit = models.CharField(max_length=20)
    smallest_units = models.PositiveIntegerField()
    buying_price = models.FloatField()
    selling_price = models.FloatField(default=0)
    
    def __str__(self):
        return f"{self.unit} - {self.smallest_units} {self.item.smallest_unit} of {self.item.name}"

class ItemKit(models.Model):
    name = models.CharField(max_length=200)
    items = models.ManyToManyField(Item, through='ItemKitItem')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="Active")
    selling_price = models.FloatField(default=0)
    
    def deactivate(self):
        self.status = "Inactive"
        self.save()

    def total_cost(self):
        """Calculate total buying price of all items in the kit."""
        return sum(
            itemkititem.item.buying_price * itemkititem.quantity
            for itemkititem in self.itemkititem_set.all()
        )
    
    def __str__(self):
        return f"{self.name} | Selling Price: {self.selling_price}"

class ItemKitItem(models.Model):
    item_kit = models.ForeignKey(ItemKit, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def subtotal(self):
        """Calculate the subtotal cost for this item in the kit."""
        return self.item.buying_price * self.quantity
    
    def __str__(self):
        return f"Kit: {self.item_kit.name} | Item: {self.item.name} | Qty: {self.quantity}"

class Adjustment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    user_responsible = models.ForeignKey(Employee, on_delete=models.CASCADE)
    in_store = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    sale_point = models.ForeignKey(SalePoint, on_delete=models.SET_NULL, null=True, blank=True)

    def update_stock(self):
        if self.store:
            self.store.update_stock(self.quantity,self.item)
        elif self.sale_point:
            self.sale_point.update_stock(self.quantity,self.item)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_stock()

    def __str__(self):
        return f"{self.item.name} | Date: {self.date} | Adj Qty: {self.quantity}"

class Requisition(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='RequisitionItem')
    user_responsible = models.ForeignKey(Employee, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Employee, null=True,default=None,on_delete=models.SET_NULL, related_name='requisition_approved_by')
    approved_date = models.DateTimeField(null=True, blank=True)
    funded = models.BooleanField(default=False)
    funded_date = models.DateTimeField(null=True, blank=True)
    funded_by = models.ForeignKey(Employee, null=True,default=None,on_delete=models.SET_NULL, related_name='requisition_funded_by')

    def total_cost(self):
        return sum(item.total_cost for item in self.requisitionitem_set.all())
    
    def __str__(self):
        return f"Dept: {self.department} | Approved: {self.approved}"

class RequisitionItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    available_stock = models.IntegerField()
    unit = models.ForeignKey(ItemUnit,on_delete=models.CASCADE)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_cost = models.FloatField()
    total_cost = models.FloatField()

    def __str__(self):
        return f"{self.item.name} | Req Qty: {self.quantity}"

class Receiving(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='ReceivedItem')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    user_responsible = models.ForeignKey(Employee, on_delete=models.CASCADE)
    is_store = models.BooleanField(default=True)
    store = models.ForeignKey(Store, null=True,on_delete=models.SET_NULL,blank=True)
    sale_point = models.ForeignKey(SalePoint, null=True, on_delete=models.SET_NULL,blank=True)

    def __str__(self):
        return f"Receiving on {self.date} | Supplier: {self.supplier.name}"

    def edit(self):
        print("editing")
    
    def total_cost(self):
        return sum(item.total_cost for item in self.receiveditem_set.all())
    
    def save(self,*args, **kwargs):
        if self.is_store is True:
            self.sale_point = None
        else:
            self.store = None
        if self.pk:
            self.edit()
        super().save(*args, **kwargs)
    
class ReceivedItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    receiving = models.ForeignKey(Receiving, on_delete=models.CASCADE)
    unit = models.ForeignKey(ItemUnit, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    total_cost = models.FloatField()

    def update_stock(self):
        qty = self.quantity * self.unit.smallest_units
        if self.receiving.is_store is True:
            self.receiving.store.update_stock(qty,self.item)
        else:
            self.receiving.sale_point.update_stock(qty,self.item)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_stock()

    def __str__(self):
        return f"{self.item.name} | Received Qty: {self.quantity}"

class Transfer(models.Model):
    TRANSFER_TYPES = (
        ('store_to_store', 'Store to Store'),
        ('salepoint_to_salepoint', 'Sale Point to Sale Point'),
        ('salepoint_to_store', 'Sale Point to Store'),
    )
    
    date = models.DateTimeField(auto_now_add=True)
    transfer_type = models.CharField(max_length=30, choices=TRANSFER_TYPES)
    from_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transfers_from', null=True, blank=True)
    to_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transfers_to', null=True, blank=True)
    from_salepoint = models.ForeignKey(SalePoint, on_delete=models.CASCADE, related_name='transfers_from', null=True, blank=True)
    to_salepoint = models.ForeignKey(SalePoint, on_delete=models.CASCADE, related_name='transfers_to', null=True, blank=True)
    items = models.ManyToManyField(Item, through='TransferItem')
    user_responsible = models.ForeignKey(Employee, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        if self.transfer_type == 'store_to_store':
            return f"Transfer from {self.from_store.name} to {self.to_store.name} on {self.date}"
        elif self.transfer_type == 'salepoint_to_salepoint':
            return f"Transfer from {self.from_salepoint.name} to {self.to_salepoint.name} on {self.date}"
        else:
            return f"Transfer from {self.from_salepoint.name} to {self.to_store.name} on {self.date}"
    
    def complete_transfer(self):
        if self.completed:
            return
            
        with transaction.atomic():
            for transfer_item in self.transferitem_set.all():
                qty = transfer_item.quantity * transfer_item.unit.smallest_units
                
                # Deduct from source
                if self.transfer_type == 'store_to_store':
                    self.from_store.update_stock(-qty, transfer_item.item)
                    self.to_store.update_stock(qty, transfer_item.item)
                elif self.transfer_type == 'salepoint_to_salepoint':
                    self.from_salepoint.update_stock(-qty, transfer_item.item)
                    self.to_salepoint.update_stock(qty, transfer_item.item)
                elif self.transfer_type == 'salepoint_to_store':
                    self.from_salepoint.update_stock(-qty, transfer_item.item)
                    self.to_store.update_stock(qty, transfer_item.item)
            
            self.completed = True
            self.save()

class TransferItem(models.Model):
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    unit = models.ForeignKey(ItemUnit, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    
    def __str__(self):
        return f"{self.item.name} | Transfer Qty: {self.quantity} {self.unit.unit}"

# Update the Issue model to better handle the workflow
class Issue(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    date = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    sale_point = models.ForeignKey(SalePoint, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='IssuedItem')
    requested_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='issues_requested')
    approved_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='issues_approved', null=True, blank=True)
    completed_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='issues_completed', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Issue from {self.store.name} to {self.sale_point.name} ({self.get_status_display()})"
    
    def approve(self, employee):
        print("Approving cond check")
        if self.status == 'pending':
            print("Cond Passed")
            self.status = 'approved'
            self.approved_by = employee
            self.save()
            print(f"After Save : {self.status}")
        else:
            print(f"Condition Failed {self.status}")
    def reject(self, employee):
        if self.status == 'pending':
            self.status = 'rejected'
            self.approved_by = employee
            self.save()
    
    def complete(self, employee):
        if self.status == 'approved' and not self.completed_date:
            with transaction.atomic():
                for issued_item in self.issueditem_set.all():
                    qty = issued_item.quantity * issued_item.unit.smallest_units
                    self.store.update_stock(-qty, issued_item.item)
                    self.sale_point.update_stock(qty, issued_item.item)
                
                self.status = 'completed'
                self.completed_by = employee
                self.completed_date = timezone.now()
                self.save()

class IssuedItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    unit = models.ForeignKey(ItemUnit, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    
    def __str__(self):
        return f"{self.item.name} | Issue Qty: {self.quantity} {self.unit.unit}"    