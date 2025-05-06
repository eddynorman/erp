from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from company.models import Department
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime

class Asset(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('under_maintenance', 'Under Maintenance'),
        ('disposed', 'Disposed'),
        ('reserved', 'Reserved'),
        ('lost', 'Lost'),
    ]
    CATEGORY_CHOICES = [
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('software', 'Software'),
        ('building', 'Building'),
        ('land', 'Land'),
        ('other', 'Other'),
    ]
    TYPE_CHOICES = [
        ('fixed', 'Fixed Asset'),
        ('current', 'Current Asset'),
        ('intangible', 'Intangible Asset'),
    ]
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    name = models.CharField(max_length=255)
    asset_tag = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='equipment')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    asset_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='fixed')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    initial_purchase_date = models.DateField()
    latest_purchase_date = models.DateField(default=None, null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=1)
    quantity_damaged = models.PositiveIntegerField(default=0)
    quantity_disposed = models.PositiveIntegerField(default=0)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    initial_supplier = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    expected_lifespan = models.PositiveIntegerField(help_text="Expected lifespan in months", null=True, blank=True)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
                                          validators=[MinValueValidator(0), MaxValueValidator(100)])
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assets')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.asset_tag})"

    def available_quantity(self):
        return self.quantity - self.quantity_damaged - self.quantity_disposed

    def calculate_depreciation(self):
        if self.expected_lifespan and self.initial_purchase_date:
            months_elapsed = (timezone.now().date() - self.initial_purchase_date).days / 30
            if months_elapsed > 0:
                depreciation_amount = (self.purchase_cost * self.depreciation_rate / 100) * (months_elapsed / 12)
                self.current_value = max(0, self.purchase_cost - depreciation_amount)
                self.save()

    def schedule_maintenance(self, days_interval):
        if self.last_maintenance_date:
            self.next_maintenance_date = self.last_maintenance_date + datetime.timedelta(days=days_interval)
            self.save()

    def is_maintenance_due(self):
        if self.next_maintenance_date:
            return timezone.now().date() >= self.next_maintenance_date
        return False

    def get_maintenance_status(self):
        if not self.next_maintenance_date:
            return "No maintenance scheduled"
        days_until = (self.next_maintenance_date - timezone.now().date()).days
        if days_until < 0:
            return f"Overdue by {abs(days_until)} days"
        elif days_until <= 7:
            return f"Due in {days_until} days"
        else:
            return f"Scheduled in {days_until} days"

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
        
    class Meta:
        ordering = ['name']
        permissions = [
            ("can_manage_assets", "Can manage assets"),
            ("can_view_assets", "Can view assets"),
            ("can_assign_assets", "Can assign assets"),
        ]

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

class AssetLocation(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='locations')
    building = models.CharField(max_length=255)
    floor = models.CharField(max_length=50)
    room = models.CharField(max_length=100)
    shelf = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    date_assigned = models.DateField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.asset.name} - {self.building}, {self.floor}, {self.room}"

class AssetWarranty(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='warranties')
    provider = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    coverage_details = models.TextField()
    warranty_number = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset.name} - {self.provider} Warranty"

    def is_valid(self):
        return self.is_active and timezone.now().date() <= self.end_date

class AssetInsurance(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='insurance_policies')
    provider = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    premium_amount = models.DecimalField(max_digits=12, decimal_places=2)
    coverage_details = models.TextField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset.name} - {self.provider} Insurance"

    def is_valid(self):
        return self.is_active and timezone.now().date() <= self.end_date

class MaintenanceSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('biannual', 'Biannual'),
        ('annual', 'Annual'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_schedules')
    maintenance_type = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    last_performed = models.DateField(null=True, blank=True)
    next_due = models.DateField()
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.asset.name} - {self.maintenance_type}"

    def calculate_next_due(self):
        if self.last_performed:
            if self.frequency == 'daily':
                self.next_due = self.last_performed + datetime.timedelta(days=1)
            elif self.frequency == 'weekly':
                self.next_due = self.last_performed + datetime.timedelta(weeks=1)
            elif self.frequency == 'monthly':
                self.next_due = self.last_performed + datetime.timedelta(days=30)
            elif self.frequency == 'quarterly':
                self.next_due = self.last_performed + datetime.timedelta(days=90)
            elif self.frequency == 'biannual':
                self.next_due = self.last_performed + datetime.timedelta(days=180)
            elif self.frequency == 'annual':
                self.next_due = self.last_performed + datetime.timedelta(days=365)
            self.save()

class MaintenanceRecord(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    schedule = models.ForeignKey(MaintenanceSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    maintenance_type = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.TextField()
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    parts_replaced = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset.name} - {self.maintenance_type} ({self.start_date})"

    def complete_maintenance(self, findings, recommendations, parts_replaced, cost):
        self.status = 'completed'
        self.end_date = timezone.now()
        self.findings = findings
        self.recommendations = recommendations
        self.parts_replaced = parts_replaced
        self.cost = cost
        self.save()
        
        # Update asset's last maintenance date
        self.asset.last_maintenance_date = self.end_date.date()
        self.asset.save()
        
        # Update maintenance schedule if exists
        if self.schedule:
            self.schedule.last_performed = self.end_date.date()
            self.schedule.calculate_next_due()

class AssetDocument(models.Model):
    DOCUMENT_TYPES = [
        ('manual', 'User Manual'),
        ('warranty', 'Warranty Document'),
        ('invoice', 'Invoice'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='asset_documents/')
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.asset.name} - {self.title}"

class AssetTransfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='transfers')
    from_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='transfers_from')
    to_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='transfers_to')
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_from')
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_to')
    transfer_date = models.DateTimeField(auto_now_add=True)
    transferred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_processed')
    reason = models.TextField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset.name} - {self.from_department} to {self.to_department}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update asset's department and assigned user
        self.asset.department = self.to_department
        self.asset.assigned_to = self.to_user
        self.asset.save()
