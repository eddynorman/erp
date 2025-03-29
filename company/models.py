from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Company(models.Model):
    company_name = models.CharField(max_length=200)
    company_email = models.EmailField()
    company_phone = models.CharField(max_length=20)
    company_location = models.CharField(max_length=200)
    
    def __str__(self):
        return self.company_name
    
    
class Branch(models.Model):
    branch_name = models.CharField(max_length=100)
    branch_location = models.CharField(max_length=200)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.branch_name

class Department(models.Model):
    department_name = models.CharField(max_length=100)
    department_description = models.TextField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE) 
    
    def __str__(self):
        return self.department_name
    
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_description = models.TextField()
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.category_name
    

class Employee(models.Model):
    employee_name = models.CharField(max_length=100)
    employee_email = models.EmailField()
    employee_phone = models.CharField(max_length=16)
    employee_address = models.CharField(max_length=200)
    employee_department = models.ForeignKey(Department,on_delete=models.CASCADE)
    employee_branch = models.ForeignKey(Branch,on_delete=models.CASCADE)
    employee_position = models.CharField(max_length=100)
    employee_salary = models.FloatField()
    employee_status = models.CharField(max_length=100, default="Active")

    def __str__(self):
        return self.employee_name
    
    def deactivate_employee(self):
        self.employee_status = "Deactivated"
        self.save()


@receiver(post_save, sender=Company)
def create_main_branch(sender, instance, created, **kwargs):
    if created:
        Branch.objects.create(
            branch_name="Main(HQ)", 
            branch_location=instance.company_location, 
            company=instance
        )