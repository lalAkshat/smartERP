from django.shortcuts import render
from .models import Employee, Department


def dashboard(request):
    employees = Employee.objects.all().order_by('-id')
    departments = Department.objects.all()

    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    total_salary = sum(employee.salary for employee in employees)

    context = {
        'employees': employees,
        'departments': departments,
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_salary': total_salary,
    }

    return render(request, 'employees/dashboard.html', context)