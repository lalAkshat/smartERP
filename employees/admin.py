from django.contrib import admin
from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'salary', 'department', 'joining_date')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('department',)
    ordering = ('name',)