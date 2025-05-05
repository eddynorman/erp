from django.contrib import admin
from .models import Company, Branch, Department, Category, Employee

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_email', 'company_phone', 'company_location')
    search_fields = ('company_name', 'company_email', 'company_location')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'branch_location', 'company')
    list_filter = ('company',)
    search_fields = ('branch_name', 'branch_location')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'branch')
    list_filter = ('branch',)
    search_fields = ('department_name', 'department_description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'department')
    list_filter = ('department',)
    search_fields = ('category_name', 'category_description')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'employee_email', 'employee_department', 'employee_branch', 'employee_status')
    list_filter = ('employee_status', 'employee_department', 'employee_branch')
    search_fields = ('employee_name', 'employee_email', 'first_name', 'last_name')
