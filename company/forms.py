from django import forms

from .models import Employee, Branch, Department, Company, Category

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'company_name',
            'company_email',
            'company_phone',
            'company_location'
        ]
        
class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = [
            'branch_name',
            'branch_location',
            'company'
        ]

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = [
            'department_name',
            'branch',
            'department_description',
        ]
        widgets = {
            'department_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
    

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'category_name',
            'department',
            'category_description',
        ]
        widgets = {
            'department_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_name',
            'employee_email',
            'employee_phone',
            'employee_address',
            'employee_branch',
            'employee_department',
            'employee_position',
            'employee_salary'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_branch'].queryset = Branch.objects.all()
        self.fields['employee_department'].queryset = Department.objects.none()

        if 'employee_branch' in self.data:
            try:
                branch_id = int(self.data.get('employee_branch'))
                self.fields['employee_department'].queryset = Department.objects.filter(branch=branch_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['employee_department'].queryset = Department.objects.filter(branch=self.instance.employee_branch)