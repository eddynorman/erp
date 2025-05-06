"""
Sales Management Tests

This module defines the tests for the sales management system.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import (
    Customer, Sale, SaleItem, SaleKit, Payment, Return,
    ReturnItem, ReturnKit, Discount, Tax, SalesPerson
)
from inventory.models import Item, ItemKit, SalePoint, SalePointItem
from company.models import Department, Category, Employee, Branch

class SalesTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        # Create test department and category
        self.department = Department.objects.create(name='Test Department')
        self.category = Category.objects.create(name='Test Category')

        # Create test branch
        self.branch = Branch.objects.create(
            name='Test Branch',
            address='Test Address',
            contact_number='1234567890'
        )

        # Create test employee
        self.employee = Employee.objects.create(
            name='Test Employee',
            department=self.department,
            branch=self.branch,
            contact_number='1234567890'
        )

        # Create test sale point
        self.sale_point = SalePoint.objects.create(
            name='Test Sale Point',
            address='Test Address',
            branch=self.branch,
            contact_person=self.employee,
            contact_number='1234567890'
        )

        # Create test item
        self.item = Item.objects.create(
            name='Test Item',
            department=self.department,
            category=self.category,
            buying_price=Decimal('10.00'),
            selling_price=Decimal('15.00'),
            smallest_unit='piece',
            is_sellable=True
        )

        # Create test kit
        self.kit = ItemKit.objects.create(
            name='Test Kit',
            department=self.department,
            category=self.category,
            selling_price=Decimal('25.00')
        )

        # Add item to kit
        self.kit.items.add(self.item)

        # Create test customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            phone='1234567890',
            email='test@example.com',
            credit_limit=Decimal('1000.00')
        )

        # Create test sales person
        self.sales_person = SalesPerson.objects.create(
            employee=self.employee,
            branch=self.branch
        )

        # Add stock to sale point
        SalePointItem.objects.create(
            sale_point=self.sale_point,
            item=self.item,
            quantity=100
        )

    def test_customer_creation(self):
        """Test customer creation"""
        self.assertEqual(self.customer.name, 'Test Customer')
        self.assertEqual(self.customer.phone, '1234567890')
        self.assertEqual(self.customer.email, 'test@example.com')
        self.assertEqual(self.customer.credit_limit, Decimal('1000.00'))

    def test_sale_creation(self):
        """Test sale creation"""
        sale = Sale.objects.create(
            invoice_number='INV001',
            customer=self.customer,
            sale_point=self.sale_point,
            sales_person=self.employee,
            payment_method='cash'
        )

        self.assertEqual(sale.customer, self.customer)
        self.assertEqual(sale.sale_point, self.sale_point)
        self.assertEqual(sale.sales_person, self.employee)
        self.assertEqual(sale.payment_method, 'cash')
        self.assertEqual(sale.payment_status, 'pending')

    def test_sale_item_addition(self):
        """Test adding items to a sale"""
        sale = Sale.objects.create(
            invoice_number='INV001',
            customer=self.customer,
            sale_point=self.sale_point,
            sales_person=self.employee,
            payment_method='cash'
        )

        sale_item = SaleItem.objects.create(
            sale=sale,
            item=self.item,
            quantity=5,
            unit_price=Decimal('15.00')
        )

        self.assertEqual(sale_item.sale, sale)
        self.assertEqual(sale_item.item, self.item)
        self.assertEqual(sale_item.quantity, 5)
        self.assertEqual(sale_item.unit_price, Decimal('15.00'))
        self.assertEqual(sale_item.total_price, Decimal('75.00'))

        # Check if stock was updated
        stock = SalePointItem.objects.get(sale_point=self.sale_point, item=self.item)
        self.assertEqual(stock.quantity, 95)

    def test_sale_kit_addition(self):
        """Test adding kits to a sale"""
        sale = Sale.objects.create(
            invoice_number='INV001',
            customer=self.customer,
            sale_point=self.sale_point,
            sales_person=self.employee,
            payment_method='cash'
        )

        sale_kit = SaleKit.objects.create(
            sale=sale,
            kit=self.kit,
            quantity=2,
            unit_price=Decimal('25.00')
        )

        self.assertEqual(sale_kit.sale, sale)
        self.assertEqual(sale_kit.kit, self.kit)
        self.assertEqual(sale_kit.quantity, 2)
        self.assertEqual(sale_kit.unit_price, Decimal('25.00'))
        self.assertEqual(sale_kit.total_price, Decimal('50.00'))

        # Check if stock was updated
        stock = SalePointItem.objects.get(sale_point=self.sale_point, item=self.item)
        self.assertEqual(stock.quantity, 98)  # 100 - (2 * 1)

    def test_payment_addition(self):
        """Test adding payments to a sale"""
        sale = Sale.objects.create(
            invoice_number='INV001',
            customer=self.customer,
            sale_point=self.sale_point,
            sales_person=self.employee,
            payment_method='cash'
        )

        SaleItem.objects.create(
            sale=sale,
            item=self.item,
            quantity=5,
            unit_price=Decimal('15.00')
        )

        payment = Payment.objects.create(
            sale=sale,
            amount=Decimal('75.00'),
            payment_method='cash'
        )

        self.assertEqual(payment.sale, sale)
        self.assertEqual(payment.amount, Decimal('75.00'))
        self.assertEqual(payment.payment_method, 'cash')

        # Check if payment status was updated
        sale.refresh_from_db()
        self.assertEqual(sale.payment_status, 'paid')

    def test_return_creation(self):
        """Test return creation"""
        sale = Sale.objects.create(
            invoice_number='INV001',
            customer=self.customer,
            sale_point=self.sale_point,
            sales_person=self.employee,
            payment_method='cash'
        )

        SaleItem.objects.create(
            sale=sale,
            item=self.item,
            quantity=5,
            unit_price=Decimal('15.00')
        )

        Payment.objects.create(
            sale=sale,
            amount=Decimal('75.00'),
            payment_method='cash'
        )

        return_obj = Return.objects.create(
            sale=sale,
            customer=self.customer,
            return_number='RET001',
            reason='Test return'
        )

        self.assertEqual(return_obj.sale, sale)
        self.assertEqual(return_obj.customer, self.customer)
        self.assertEqual(return_obj.return_number, 'RET001')
        self.assertEqual(return_obj.reason, 'Test return')
        self.assertEqual(return_obj.status, 'pending')

    def test_return_item_addition(self):
        """Test adding items to a return"""
        sale = Sale.objects.create(
            invoice_number='INV001',
            customer=self.customer,
            sale_point=self.sale_point,
            sales_person=self.employee,
            payment_method='cash'
        )

        SaleItem.objects.create(
            sale=sale,
            item=self.item,
            quantity=5,
            unit_price=Decimal('15.00')
        )

        Payment.objects.create(
            sale=sale,
            amount=Decimal('75.00'),
            payment_method='cash'
        )

        return_obj = Return.objects.create(
            sale=sale,
            customer=self.customer,
            return_number='RET001',
            reason='Test return'
        )

        return_item = ReturnItem.objects.create(
            return_obj=return_obj,
            item=self.item,
            quantity=2,
            unit_price=Decimal('15.00')
        )

        self.assertEqual(return_item.return_obj, return_obj)
        self.assertEqual(return_item.item, self.item)
        self.assertEqual(return_item.quantity, 2)
        self.assertEqual(return_item.unit_price, Decimal('15.00'))
        self.assertEqual(return_item.total_price, Decimal('30.00'))

        # Check if stock was updated
        stock = SalePointItem.objects.get(sale_point=self.sale_point, item=self.item)
        self.assertEqual(stock.quantity, 97)  # 100 - 5 + 2

    def test_discount_creation(self):
        """Test discount creation"""
        discount = Discount.objects.create(
            name='Test Discount',
            percentage=Decimal('10.00'),
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )

        self.assertEqual(discount.name, 'Test Discount')
        self.assertEqual(discount.percentage, Decimal('10.00'))
        self.assertTrue(discount.is_active)

    def test_tax_creation(self):
        """Test tax creation"""
        tax = Tax.objects.create(
            name='VAT',
            percentage=Decimal('16.00')
        )

        self.assertEqual(tax.name, 'VAT')
        self.assertEqual(tax.percentage, Decimal('16.00'))
        self.assertTrue(tax.is_active)

    def test_salesperson_stats(self):
        """Test salesperson statistics"""
        sale = Sale.objects.create(
            invoice_number='INV001',
            customer=self.customer,
            sale_point=self.sale_point,
            sales_person=self.employee,
            payment_method='cash'
        )

        SaleItem.objects.create(
            sale=sale,
            item=self.item,
            quantity=5,
            unit_price=Decimal('15.00')
        )

        Payment.objects.create(
            sale=sale,
            amount=Decimal('75.00'),
            payment_method='cash'
        )

        self.sales_person.refresh_from_db()
        self.assertEqual(self.sales_person.total_sales, Decimal('75.00'))
        self.assertEqual(self.sales_person.total_returns, Decimal('0.00'))
        self.assertEqual(self.sales_person.net_sales, Decimal('75.00'))

        # Add a return
        return_obj = Return.objects.create(
            sale=sale,
            customer=self.customer,
            return_number='RET001',
            reason='Test return'
        )

        ReturnItem.objects.create(
            return_obj=return_obj,
            item=self.item,
            quantity=2,
            unit_price=Decimal('15.00')
        )

        self.sales_person.refresh_from_db()
        self.assertEqual(self.sales_person.total_sales, Decimal('75.00'))
        self.assertEqual(self.sales_person.total_returns, Decimal('30.00'))
        self.assertEqual(self.sales_person.net_sales, Decimal('45.00'))
