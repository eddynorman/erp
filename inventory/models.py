from django.db import models
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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    store_stock = models.IntegerField(default=0)
    shop_stock = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="Active")
    buying_price = models.FloatField(default=0)
    selling_price = models.FloatField(default=0)
    smallest_unit = models.CharField(max_length=20)   
    is_sellable = models.BooleanField(default=True)
    minimum_stock = models.IntegerField(default=0)
    optimum_stock = models.IntegerField(default=0)

    def adjust_stock(self, qty, is_store=True):
        """Adjust stock based on whether it is store or shop"""
        if is_store:
            self.store_stock += qty
        else:
            self.shop_stock += qty
        self.save()

    def total_stock(self):
        return self.store_stock + self.shop_stock

    def __str__(self):
        return f"{self.name} | Store: {self.store_stock} | Shop: {self.shop_stock} | Total: {self.total_stock()}"

class StoreItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class ItemOtherUnit(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    unit = models.CharField(max_length=20)
    conversion_factor = models.FloatField()

class ItemKit(models.Model):
    name = models.CharField(max_length=200)
    items = models.ManyToManyField(Item, through='ItemKitItem')
    status = models.CharField(max_length=20, default="Active")
    selling_price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} | Selling Price: {self.selling_price}"

class ItemKitItem(models.Model):
    item_kit = models.ForeignKey(ItemKit, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Kit: {self.item_kit.name} | Item: {self.item.name} | Qty: {self.quantity}"

class Adjustment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    user_responsible = models.ForeignKey(Employee, on_delete=models.CASCADE)
    in_store = models.BooleanField(default=True)

    def update_stock(self):
        self.item.adjust_stock(self.quantity, self.in_store)

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
