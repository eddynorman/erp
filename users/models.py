from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from company.models import Employee

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class CustomGroup(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.group.name

class GroupPermission(models.Model):
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'permission')

    def __str__(self):
        return f"{self.group.group.name} - {self.permission.name}"

class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} - {self.group.group.name}"
