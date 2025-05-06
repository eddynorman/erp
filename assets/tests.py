from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta
from .models import (
    Asset, AssetPurchase, DamagedAsset, DisposedAsset, AssetRepair,
    AssetLocation, AssetWarranty, AssetInsurance, MaintenanceSchedule,
    MaintenanceRecord, AssetDocument, AssetTransfer
)

class AssetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_tag='TAG001',
            category='Equipment',
            description='Test Description',
            quantity=10,
            purchase_cost=1000.00,
            initial_purchase_date=timezone.now().date(),
            initial_supplier='Test Supplier',
            department='IT',
            condition='good',
            expected_lifespan=5,
            depreciation_rate=20,
            created_by=self.user
        )

    def test_asset_creation(self):
        self.assertEqual(self.asset.name, 'Test Asset')
        self.assertEqual(self.asset.asset_tag, 'TAG001')
        self.assertEqual(self.asset.quantity, 10)
        self.assertEqual(self.asset.purchase_cost, 1000.00)

    def test_asset_depreciation(self):
        self.asset.calculate_depreciation()
        self.assertEqual(self.asset.current_value, 800.00)  # 20% depreciation

    def test_asset_maintenance_status(self):
        self.asset.next_maintenance_date = timezone.now().date() + timedelta(days=7)
        self.assertEqual(self.asset.get_maintenance_status(), 'Scheduled')

class AssetViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test asset
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_tag='TAG001',
            category='Equipment',
            description='Test Description',
            quantity=10,
            purchase_cost=1000.00,
            initial_purchase_date=timezone.now().date(),
            initial_supplier='Test Supplier',
            department='IT',
            created_by=self.user
        )

    def test_asset_list_view(self):
        response = self.client.get(reverse('assets:asset_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assets/asset_list.html')
        self.assertContains(response, 'Test Asset')

    def test_asset_detail_view(self):
        response = self.client.get(reverse('assets:asset_detail', args=[self.asset.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assets/asset_detail.html')
        self.assertContains(response, 'Test Asset')

    def test_add_asset_view(self):
        response = self.client.post(reverse('assets:add_asset'), {
            'name': 'New Asset',
            'asset_tag': 'TAG002',
            'category': 'Equipment',
            'description': 'New Description',
            'quantity': 5,
            'purchase_cost': 500.00,
            'initial_purchase_date': timezone.now().date(),
            'initial_supplier': 'New Supplier',
            'department': 'IT'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Asset.objects.filter(name='New Asset').exists())

class AssetPurchaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_tag='TAG001',
            category='Equipment',
            description='Test Description',
            quantity=10,
            purchase_cost=1000.00,
            initial_purchase_date=timezone.now().date(),
            initial_supplier='Test Supplier',
            department='IT',
            created_by=self.user
        )

    def test_purchase_creation(self):
        purchase = AssetPurchase.objects.create(
            asset=self.asset,
            purchase_date=timezone.now().date(),
            quantity=5,
            price=500.00,
            supplier='New Supplier'
        )
        self.assertEqual(purchase.quantity, 5)
        self.assertEqual(purchase.price, 500.00)
        self.assertEqual(self.asset.quantity, 15)  # Original 10 + new 5

class MaintenanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_tag='TAG001',
            category='Equipment',
            description='Test Description',
            quantity=10,
            purchase_cost=1000.00,
            initial_purchase_date=timezone.now().date(),
            initial_supplier='Test Supplier',
            department='IT',
            created_by=self.user
        )

    def test_maintenance_schedule(self):
        schedule = MaintenanceSchedule.objects.create(
            asset=self.asset,
            maintenance_type='preventive',
            frequency=30,  # days
            last_performed=timezone.now().date(),
            next_due=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(schedule.maintenance_type, 'preventive')
        self.assertEqual(schedule.frequency, 30)

    def test_maintenance_record(self):
        record = MaintenanceRecord.objects.create(
            asset=self.asset,
            maintenance_type='preventive',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=2),
            cost=100.00,
            performed_by='Test Technician',
            status='completed',
            notes='Test maintenance completed'
        )
        self.assertEqual(record.status, 'completed')
        self.assertEqual(record.cost, 100.00)

class AssetTransferTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_tag='TAG001',
            category='Equipment',
            description='Test Description',
            quantity=10,
            purchase_cost=1000.00,
            initial_purchase_date=timezone.now().date(),
            initial_supplier='Test Supplier',
            department='IT',
            created_by=self.user
        )

    def test_asset_transfer(self):
        transfer = AssetTransfer.objects.create(
            asset=self.asset,
            from_department='IT',
            to_department='HR',
            transfer_date=timezone.now().date(),
            transferred_by=self.user,
            reason='Department reorganization'
        )
        self.assertEqual(transfer.from_department, 'IT')
        self.assertEqual(transfer.to_department, 'HR')
        self.assertEqual(self.asset.department, 'HR')  # Asset department should be updated

class AssetWarrantyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_tag='TAG001',
            category='Equipment',
            description='Test Description',
            quantity=10,
            purchase_cost=1000.00,
            initial_purchase_date=timezone.now().date(),
            initial_supplier='Test Supplier',
            department='IT',
            created_by=self.user
        )

    def test_warranty_creation(self):
        warranty = AssetWarranty.objects.create(
            asset=self.asset,
            provider='Test Provider',
            warranty_number='WARR001',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            coverage_details='Full coverage',
            is_active=True
        )
        self.assertEqual(warranty.provider, 'Test Provider')
        self.assertEqual(warranty.warranty_number, 'WARR001')
        self.assertTrue(warranty.is_active)

class AssetInsuranceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_tag='TAG001',
            category='Equipment',
            description='Test Description',
            quantity=10,
            purchase_cost=1000.00,
            initial_purchase_date=timezone.now().date(),
            initial_supplier='Test Supplier',
            department='IT',
            created_by=self.user
        )

    def test_insurance_creation(self):
        insurance = AssetInsurance.objects.create(
            asset=self.asset,
            provider='Test Insurance',
            policy_number='POL001',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            coverage_amount=5000.00,
            premium_amount=500.00,
            coverage_details='Full coverage',
            is_active=True
        )
        self.assertEqual(insurance.provider, 'Test Insurance')
        self.assertEqual(insurance.policy_number, 'POL001')
        self.assertEqual(insurance.coverage_amount, 5000.00)
        self.assertTrue(insurance.is_active)

class AssetDocumentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_tag='TAG001',
            category='Equipment',
            description='Test Description',
            quantity=10,
            purchase_cost=1000.00,
            initial_purchase_date=timezone.now().date(),
            initial_supplier='Test Supplier',
            department='IT',
            created_by=self.user
        )

    def test_document_creation(self):
        document = AssetDocument.objects.create(
            asset=self.asset,
            document_type='manual',
            title='Test Manual',
            file_path='/path/to/manual.pdf',
            upload_date=timezone.now().date(),
            uploaded_by=self.user,
            description='Test document description'
        )
        self.assertEqual(document.document_type, 'manual')
        self.assertEqual(document.title, 'Test Manual')
        self.assertEqual(document.uploaded_by, self.user)
