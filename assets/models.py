from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from company.models import Department

class Asset(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('under_maintenance', 'Under Maintenance'),
        ('disposed', 'Disposed'),
    ]
    CATEGORY_CHOICES = [
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('software', 'Software'),
        ('other', 'Other'),
    ]
    TYPE_CHOICES = [
        ('fixed asset', 'Fixed Asset'),
        ('current asset', 'Current Asset'),
    ]
    
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES,default='Equipment')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Current Asset')
    initial_purchase_date = models.DateField()
    latest_purchase_date = models.DateField(default=None, null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Total cost of all purchases
    quantity = models.PositiveIntegerField(default=1)  # Total quantity purchased
    quantity_damaged = models.PositiveIntegerField(default=0)  # Damaged items
    quantity_disposed = models.PositiveIntegerField(default=0)  # Disposed items
    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    initial_supplier = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - Total: {self.quantity}, Damaged: {self.quantity_damaged}, Disposed: {self.quantity_disposed}"

    def available_quantity(self):
        """Returns the number of usable assets (not damaged or disposed)."""
        return self.quantity - self.quantity_damaged - self.quantity_disposed

    def dispose_items(self, count):
        """Mark a given number of items as disposed."""
        if count > self.quantity_damaged():
            raise ValueError("Cannot dispose more than available damaged quantity")
        self.quantity_disposed += count
        self.purchase_cost -= (count * self.getUnitPrice())
        self.save()

    def mark_damaged(self, count):
        """Mark a given number of items as damaged."""
        if count > self.available_quantity():
            raise ValueError("Cannot mark more as damaged than available")
        self.quantity_damaged += count
        self.save()

    def update_totals(self, quantity, total_price, purchase_date):
        """Update total quantity, purchase cost, and latest purchase date."""
        self.quantity += quantity
        self.purchase_cost += total_price  # Add full purchase cost
        self.latest_purchase_date = purchase_date
        self.save()
        
    def update_totals2(self, quantity, total_price, purchase_date):
        """Update total quantity, purchase cost, and latest purchase date."""
        self.quantity -= quantity
        self.purchase_cost -= total_price  # Add full purchase cost
        self.latest_purchase_date = purchase_date
        self.save()
        
    def getUnitPrice(self):
        if self.quantity > 0:
            return self.purchase_cost / self.quantity
        return 0
    
    def update_quantity(self, quantity):
        """Update the quantity of the asset."""
        self.quantity += quantity
        self.save()
    
    def repair_asset(self, quantity):
        """Repair a given number of damaged items."""
        if quantity > self.quantity_damaged:
            raise ValueError("Cannot repair more than damaged quantity")
        self.quantity_damaged -= quantity
        self.save()
        

class AssetPurchase(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="purchases")
    purchase_date = models.DateField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)  # Total purchase price
    supplier = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.asset.name} - {self.quantity} units bought on {self.purchase_date}"

    def save(self, *args, **kwargs):
        """On save, update total quantity, cost, and latest purchase date in the Asset model."""
        super().save(*args, **kwargs)
        self.asset.update_totals(self.quantity, self.price, self.purchase_date)
    
    def edit_purchase(self, new_quantity, new_price, new_purchase_date):
        """Edit the purchase details."""
        old_quantity = self.quantity
        old_price = self.price
        self.quantity = new_quantity
        self.price = new_price
        self.save()
        self.asset.update_totals(new_quantity, new_price, new_purchase_date)

class DamagedAsset(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="damaged_assets")
    quantity = models.PositiveIntegerField()
    reason = models.TextField(default="Broken or Damaged")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset.name}, {self.quantity} units"

    def save(self, *args, **kwargs):
        """On save, update the total quantity of damaged items in the Asset model."""
        super().save(*args, **kwargs)
        self.asset.mark_damaged(self.quantity)

class AssetRepair(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="repairs")
    quantity = models.PositiveIntegerField()
    description = models.TextField(default="Repaired")
    date = models.DateField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self):
        return f"{self.asset.name}, {self.quantity} units"
    def save(self, *args, **kwargs):
        """On save, update the total quantity of damaged items in the Asset model."""
        super().save(*args, **kwargs)
        self.asset.repair_asset(self.quantity)

class DisposedAsset(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="disposed_assets")
    quantity = models.PositiveIntegerField()
    reason = models.TextField(default="Disposed")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset.name}, {self.quantity} units"

    def save(self, *args, **kwargs):
        """On save, update the total quantity of disposed items in the Asset model."""
        super().save(*args, **kwargs)
        self.asset.dispose_items(self.quantity)
        
@receiver(post_save, sender=Asset)
def create_initial_purchase(sender, instance, created, **kwargs):
    if created:
        q = instance.quantity
        p = instance.purchase_cost
        instance.update_totals2(q, instance.purchase_cost, instance.initial_purchase_date)
        AssetPurchase.objects.create(
            asset=instance,
            purchase_date=instance.initial_purchase_date,
            quantity= q,
            price=p,
            supplier=instance.initial_supplier  # You can modify this to fetch from a form
        )
