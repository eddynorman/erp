from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import (
    Asset, AssetPurchase, DamagedAsset, DisposedAsset, AssetRepair,
    AssetLocation, AssetWarranty, AssetInsurance, MaintenanceSchedule,
    MaintenanceRecord, AssetDocument, AssetTransfer
)

@receiver(post_save, sender=Asset)
def create_initial_purchase(sender, instance, created, **kwargs):
    if created:
        q = instance.quantity
        p = instance.purchase_cost
        instance.update_totals2(q, instance.purchase_cost, instance.initial_purchase_date)
        AssetPurchase.objects.create(
            asset=instance,
            purchase_date=instance.initial_purchase_date,
            quantity=q,
            price=p,
            supplier=instance.initial_supplier
        )

@receiver(pre_save, sender=Asset)
def check_maintenance_due(sender, instance, **kwargs):
    if instance.next_maintenance_date and instance.next_maintenance_date <= timezone.now().date():
        # Send email notification
        subject = f'Maintenance Due: {instance.name}'
        message = f'''
        Asset: {instance.name} ({instance.asset_tag})
        Department: {instance.department}
        Maintenance Due Date: {instance.next_maintenance_date}
        Current Status: {instance.get_maintenance_status()}
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )

@receiver(pre_save, sender=AssetWarranty)
def check_warranty_expiry(sender, instance, **kwargs):
    if instance.is_active and instance.end_date <= timezone.now().date():
        # Send email notification
        subject = f'Warranty Expired: {instance.asset.name}'
        message = f'''
        Asset: {instance.asset.name} ({instance.asset.asset_tag})
        Warranty Provider: {instance.provider}
        Warranty Number: {instance.warranty_number}
        Expiry Date: {instance.end_date}
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )

@receiver(pre_save, sender=AssetInsurance)
def check_insurance_expiry(sender, instance, **kwargs):
    if instance.is_active and instance.end_date <= timezone.now().date():
        # Send email notification
        subject = f'Insurance Expired: {instance.asset.name}'
        message = f'''
        Asset: {instance.asset.name} ({instance.asset.asset_tag})
        Insurance Provider: {instance.provider}
        Policy Number: {instance.policy_number}
        Coverage Amount: {instance.coverage_amount}
        Expiry Date: {instance.end_date}
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )

@receiver(post_save, sender=MaintenanceRecord)
def update_asset_maintenance(sender, instance, created, **kwargs):
    if created and instance.status == 'completed':
        # Update asset's last maintenance date
        instance.asset.last_maintenance_date = instance.end_date.date()
        instance.asset.save()
        
        # Update maintenance schedule if exists
        if instance.schedule:
            instance.schedule.last_performed = instance.end_date.date()
            instance.schedule.calculate_next_due()

@receiver(post_save, sender=AssetTransfer)
def notify_transfer(sender, instance, created, **kwargs):
    if created:
        # Send email notification
        subject = f'Asset Transfer: {instance.asset.name}'
        message = f'''
        Asset: {instance.asset.name} ({instance.asset.asset_tag})
        From Department: {instance.from_department}
        To Department: {instance.to_department}
        Transferred By: {instance.transferred_by}
        Date: {instance.transfer_date}
        Reason: {instance.reason}
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )

@receiver(post_save, sender=DamagedAsset)
def notify_damage(sender, instance, created, **kwargs):
    if created:
        # Send email notification
        subject = f'Asset Damaged: {instance.asset.name}'
        message = f'''
        Asset: {instance.asset.name} ({instance.asset.asset_tag})
        Department: {instance.asset.department}
        Quantity Damaged: {instance.quantity}
        Reason: {instance.reason}
        Date: {instance.date}
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )

@receiver(post_save, sender=DisposedAsset)
def notify_disposal(sender, instance, created, **kwargs):
    if created:
        # Send email notification
        subject = f'Asset Disposed: {instance.asset.name}'
        message = f'''
        Asset: {instance.asset.name} ({instance.asset.asset_tag})
        Department: {instance.asset.department}
        Quantity Disposed: {instance.quantity}
        Reason: {instance.reason}
        Date: {instance.date}
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        ) 