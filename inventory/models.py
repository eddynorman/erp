from django.db import models
from django.db.models import F
from company.models import Department, Category, Employee

# Store for storing items not in the shop/production areas
class Store(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
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
        
    def update_shop_stock(self, qty):
        """Update shop stock based on the given quantity."""
        if(qty >= 0):
            self.shop_stock += qty
            self.save()
        else:
            if self.shop_stock >= abs(qty):
                self.shop_stock += qty
                self.save()
            else:
                raise ValueError("Not enough stock in the shop to adjust.")
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

    def update_stock(self):
        if self.store:
            self.store.update_stock(self.quantity,self.item)
        else:
            self.item.update_shop_stock(self.quantity)

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
    approved_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='requisition_approved_by')
    approved_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Dept: {self.department.name} | Approved: {self.approved}"

class RequisitionItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.item.name} | Req Qty: {self.quantity}"

class Receiving(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='ReceivedItem')
    user_responsible = models.ForeignKey(Employee, on_delete=models.CASCADE)
    is_store = models.BooleanField(default=True)

    def __str__(self):
        return f"Receiving on {self.date} | Supplier: {self.supplier.name}"

class ReceivedItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    receiving = models.ForeignKey(Receiving, on_delete=models.CASCADE)
    unit = models.ForeignKey(ItemUnit, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.FloatField()

    def update_stock(self):
        self.item.adjust_stock(self.quantity, self.receiving.is_store)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_stock()

    def __str__(self):
        return f"{self.item.name} | Received Qty: {self.quantity}"

class Issue(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='IssuedItem')
    requested_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='issue_approved_by')
    to_shop = models.BooleanField(default=True)

    def __str__(self):
        return f"Issue on {self.date} | To Shop: {self.to_shop}"

class IssuedItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def update_stock(self):
        """Move stock between store and shop"""
        if self.issue.to_shop:
            self.item.adjust_stock(self.quantity, is_store=False)
            self.item.adjust_stock(-self.quantity, is_store=True)
        else:
            self.item.adjust_stock(self.quantity, is_store=True)
            self.item.adjust_stock(-self.quantity, is_store=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_stock()

    def __str__(self):
        return f"{self.item.name} | Issued Qty: {self.quantity}"
