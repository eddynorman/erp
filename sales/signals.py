"""
Sales Management Signals

This module defines the signals for the sales management system.
These signals handle automatic updates when related models change.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    Sale, SaleItem, SaleKit, Payment, Return,
    ReturnItem, ReturnKit, SalesPerson
)

@receiver([post_save, post_delete], sender=SaleItem)
@receiver([post_save, post_delete], sender=SaleKit)
def update_sale_totals(sender, instance, **kwargs):
    """
    Update sale totals when items or kits are added, modified, or deleted.
    """
    if hasattr(instance, 'sale'):
        instance.sale.calculate_totals()

@receiver([post_save, post_delete], sender=Payment)
def update_sale_payment_status(sender, instance, **kwargs):
    """
    Update sale payment status when payments are added, modified, or deleted.
    """
    if hasattr(instance, 'sale'):
        instance.sale.update_payment_status()

@receiver([post_save, post_delete], sender=ReturnItem)
@receiver([post_save, post_delete], sender=ReturnKit)
def update_return_totals(sender, instance, **kwargs):
    """
    Update return totals when items or kits are added, modified, or deleted.
    """
    if hasattr(instance, 'return_obj'):
        instance.return_obj.calculate_total()

@receiver([post_save, post_delete], sender=Sale)
@receiver([post_save, post_delete], sender=Return)
def update_salesperson_stats(sender, instance, **kwargs):
    """
    Update salesperson statistics when sales or returns are added, modified, or deleted.
    """
    if isinstance(instance, Sale):
        salesperson = SalesPerson.objects.filter(employee=instance.sales_person).first()
        if salesperson:
            salesperson.update_stats()
    elif isinstance(instance, Return):
        salesperson = SalesPerson.objects.filter(employee=instance.sale.sales_person).first()
        if salesperson:
            salesperson.update_stats() 