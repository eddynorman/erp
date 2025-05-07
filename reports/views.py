from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from .models import ReportType, ReportSchedule, ReportHistory
from .forms import ReportScheduleForm
from company.models import Company, Department, Employee
from inventory.models import Item, StoreItem, SalePointItem
from assets.models import Asset
from sales.models import Sale, SaleItem
import os
from datetime import datetime, timedelta
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

@login_required
def report_list(request):
    report_types = ReportType.objects.filter(is_active=True)
    schedules = ReportSchedule.objects.filter(user=request.user, is_active=True)
    history = ReportHistory.objects.filter(user=request.user).order_by('-generated_at')[:10]
    
    context = {
        'report_types': report_types,
        'schedules': schedules,
        'history': history,
    }
    return render(request, 'reports/report_list.html', context)

@login_required
def generate_report(request, report_type_id):
    report_type = get_object_or_404(ReportType, id=report_type_id)
    format_type = request.GET.get('format', report_type.default_format)
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        # Convert dates if provided
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate report based on type
        if report_type.name == 'Sales Report':
            data = generate_sales_report(start_date, end_date)
        elif report_type.name == 'Inventory Report':
            data = generate_inventory_report()
        elif report_type.name == 'Assets Report':
            data = generate_assets_report()
        elif report_type.name == 'Company Report':
            data = generate_company_report()
        elif report_type.name == 'Purchases Report':
            data = generate_purchases_report(start_date, end_date)
        elif report_type.name == 'Issues Report':
            data = generate_issues_report(start_date, end_date)
        else:
            raise ValueError(f"Unknown report type: {report_type.name}")
        
        # Create report file
        if format_type in ['pdf', 'both']:
            pdf_file = generate_pdf_report(data, report_type.name)
            if format_type == 'pdf':
                return FileResponse(pdf_file, as_attachment=True, filename=f"{report_type.name}_{datetime.now().strftime('%Y%m%d')}.pdf")
        
        if format_type in ['excel', 'both']:
            if isinstance(data, dict):
                excel_file = io.BytesIO()
                with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                    for key, df in data.items():
                        df.to_excel(writer, sheet_name=key.title(), index=False)
            else:
                excel_file = generate_excel_report(data, report_type.name)
            
            if format_type == 'excel':
                return FileResponse(excel_file, as_attachment=True, filename=f"{report_type.name}_{datetime.now().strftime('%Y%m%d')}.xlsx")
        
        # Save report history
        ReportHistory.objects.create(
            report_type=report_type,
            user=request.user,
            file_path=f"reports/{report_type.name}_{datetime.now().strftime('%Y%m%d')}",
            format=format_type,
            status='success',
            parameters={
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                'format': format_type
            }
        )
        
        messages.success(request, f"{report_type.name} generated successfully!")
        return redirect('reports:report_list')
        
    except ValueError as ve:
        ReportHistory.objects.create(
            report_type=report_type,
            user=request.user,
            status='failed',
            error_message=str(ve)
        )
        messages.error(request, f"Invalid input: {str(ve)}")
        return redirect('reports:report_list')
    except Exception as e:
        ReportHistory.objects.create(
            report_type=report_type,
            user=request.user,
            status='failed',
            error_message=str(e)
        )
        messages.error(request, f"Error generating report: {str(e)}")
        return redirect('reports:report_list')

@login_required
def schedule_report(request, report_type_id):
    report_type = get_object_or_404(ReportType, id=report_type_id)
    
    if request.method == 'POST':
        form = ReportScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.report_type = report_type
            schedule.user = request.user
            schedule.save()
            messages.success(request, "Report schedule created successfully!")
            return redirect('report_list')
    else:
        form = ReportScheduleForm()
    
    return render(request, 'reports/schedule_report.html', {'form': form, 'report_type': report_type})

@login_required
def dashboard(request):
    return render(request, 'reports/dashboard.html')

def generate_assets_report():
    assets = Asset.objects.all().select_related('department')
    data = []
    for asset in assets:
        data.append({
            'Asset ID': asset.asset_tag,
            'Name': asset.name,
            'Category': asset.category,
            'Status': asset.status,
            'Assigned To': asset.assigned_to.username if asset.assigned_to else 'Unassigned',
            'Purchase Date': asset.initial_purchase_date,
            'Value': float(asset.current_value),
            'Department': asset.department.name,
            'Condition': asset.condition,
            'Quantity': asset.quantity,
            'Available': asset.available_quantity()
        })
    return pd.DataFrame(data)

def generate_company_report():
    companies = Company.objects.all()
    departments = Department.objects.all()
    employees = Employee.objects.all()
    
    company_data = []
    for company in companies:
        company_data.append({
            'Company Name': company.name,
            'Registration Number': company.registration_number,
            'Tax Number': company.tax_number,
            'Address': company.address,
            'Phone': company.phone,
            'Email': company.email,
            'Website': company.website
        })
    
    department_data = []
    for dept in departments:
        department_data.append({
            'Department Name': dept.name,
            'Company': dept.company.name,
            'Manager': dept.manager.user.username if dept.manager else 'Not Assigned',
            'Description': dept.description
        })
    
    employee_data = []
    for emp in employees:
        employee_data.append({
            'Employee ID': emp.employee_id,
            'Name': f"{emp.user.first_name} {emp.user.last_name}",
            'Department': emp.department.name if emp.department else 'Not Assigned',
            'Position': emp.position,
            'Email': emp.user.email,
            'Phone': emp.phone,
            'Hire Date': emp.hire_date
        })
    
    return {
        'companies': pd.DataFrame(company_data),
        'departments': pd.DataFrame(department_data),
        'employees': pd.DataFrame(employee_data)
    }

def generate_purchases_report(start_date=None, end_date=None):
    # This would typically come from a purchases app
    # For now, we'll create a sample report with date filtering
    data = {
        'Purchase ID': ['P001', 'P002'],
        'Date': ['2024-01-01', '2024-01-02'],
        'Supplier': ['Supplier A', 'Supplier B'],
        'Items': ['Item A, Item B', 'Item C, Item D'],
        'Total Amount': [5000, 7500],
        'Status': ['Completed', 'Pending']
    }
    
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    
    if start_date:
        df = df[df['Date'] >= start_date]
    if end_date:
        df = df[df['Date'] <= end_date]
    
    return df

def generate_issues_report(start_date=None, end_date=None):
    # This would typically come from an issues/tickets app
    # For now, we'll create a sample report with date filtering
    data = {
        'Issue ID': ['I001', 'I002'],
        'Date': ['2024-01-01', '2024-01-02'],
        'Type': ['Bug', 'Feature Request'],
        'Priority': ['High', 'Medium'],
        'Status': ['Open', 'In Progress'],
        'Assigned To': ['User A', 'User B'],
        'Description': ['Issue description 1', 'Issue description 2']
    }
    
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    
    if start_date:
        df = df[df['Date'] >= start_date]
    if end_date:
        df = df[df['Date'] <= end_date]
    
    return df

def generate_inventory_report():
    items = Item.objects.all().select_related('category')
    store_items = StoreItem.objects.all().select_related('item', 'store')
    sale_point_items = SalePointItem.objects.all().select_related('item', 'sale_point')
    
    item_data = []
    for item in items:
        item_data.append({
            'Item ID': item.id,
            'Name': item.name,
            'Category': item.category.name,
            'Description': item.notes,
            'Buying Price': float(item.buying_price),
            'Selling Price': float(item.selling_price),
            'Store Stock': item.store_stock,
            'Shop Stock': item.shop_stock,
            'Total Stock': item.total_stock(),
            'Status': item.status
        })
    
    store_stock_data = []
    for item in store_items:
        store_stock_data.append({
            'Item': item.item.name,
            'Store': item.store.name,
            'Quantity': item.quantity,
            'Last Updated': item.last_updated
        })
    
    sale_point_stock_data = []
    for item in sale_point_items:
        sale_point_stock_data.append({
            'Item': item.item.name,
            'Sale Point': item.sale_point.name,
            'Quantity': item.quantity,
            'Last Updated': item.last_updated
        })
    
    return {
        'items': pd.DataFrame(item_data),
        'store_stock': pd.DataFrame(store_stock_data),
        'sale_point_stock': pd.DataFrame(sale_point_stock_data)
    }

def generate_sales_report(start_date=None, end_date=None):
    sales = Sale.objects.all().select_related('customer')
    
    # Apply date filters if provided
    if start_date:
        sales = sales.filter(date__gte=start_date)
    if end_date:
        sales = sales.filter(date__lte=end_date)
    
    sale_items = SaleItem.objects.filter(sale__in=sales).select_related('sale', 'product')
    
    sales_data = []
    for sale in sales:
        sales_data.append({
            'Sale ID': sale.sale_id,
            'Date': sale.date,
            'Customer': sale.customer.name,
            'Total Amount': sale.total_amount,
            'Status': sale.status,
            'Payment Method': sale.payment_method
        })
    
    items_data = []
    for item in sale_items:
        items_data.append({
            'Sale ID': item.sale.sale_id,
            'Product': item.product.name,
            'Quantity': item.quantity,
            'Unit Price': item.unit_price,
            'Total': item.total
        })
    
    return {
        'sales': pd.DataFrame(sales_data),
        'items': pd.DataFrame(items_data)
    }

def generate_pdf_report(data, report_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    elements.append(Paragraph(report_name, styles['Title']))
    elements.append(Spacer(1, 20))
    
    if isinstance(data, dict):
        for key, df in data.items():
            elements.append(Paragraph(key.title(), styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            # Convert DataFrame to list of lists for table
            table_data = [df.columns.tolist()] + df.values.tolist()
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))
    else:
        # Single DataFrame
        table_data = [data.columns.tolist()] + data.values.tolist()
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_excel_report(data, report_name):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Report', index=False)
    buffer.seek(0)
    return buffer
