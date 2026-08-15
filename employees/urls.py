from django.urls import path
from . import views


urlpatterns = [

    # Dashboard
    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    # Employees
    path(
        'employees/',
        views.employee_list,
        name='employee_list'
    ),

    path(
        'employees/add/',
        views.add_employee,
        name='add_employee'
    ),

    path(
        'employees/edit/<int:id>/',
        views.edit_employee,
        name='edit_employee'
    ),

    path(
        'employees/delete/<int:id>/',
        views.delete_employee,
        name='delete_employee'
    ),

    # Departments
    path(
        'departments/',
        views.department_list,
        name='department_list'
    ),

    path(
        'departments/add/',
        views.add_department,
        name='add_department'
    ),

    path(
        'departments/edit/<int:id>/',
        views.edit_department,
        name='edit_department'
    ),

    path(
        'departments/delete/<int:id>/',
        views.delete_department,
        name='delete_department'
    ),

    # Salary
    path(
        'salary/',
        views.salary_list,
        name='salary_list'
    ),

    # Reports
    path(
        'reports/',
        views.reports,
        name='reports'
    ),

    # AI Assistant
    path(
        'ai-assistant/',
        views.ai_assistant,
        name='ai_assistant'
    ),
]