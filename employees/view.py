from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, Max, Min, Count
from django.contrib.auth.decorators import login_required
import re

from .models import Employee, Department


# =====================================================
# DASHBOARD
# =====================================================

@login_required(login_url='login')
def dashboard(request):

    total_employees = Employee.objects.count()

    total_departments = Department.objects.count()

    total_salary = Employee.objects.aggregate(
        Sum('salary')
    )['salary__sum'] or 0

    recent_employees = Employee.objects.select_related(
        'department'
    ).order_by('-id')[:5]

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_salary': total_salary,
        'recent_employees': recent_employees,
    }

    return render(
        request,
        'employees/dashboard.html',
        context
    )


# =====================================================
# EMPLOYEE LIST
# =====================================================

@login_required(login_url='login')
def employee_list(request):

    employees = Employee.objects.select_related(
        'department'
    ).order_by('-id')

    return render(
        request,
        'employees/employees.html',
        {
            'employees': employees
        }
    )


# =====================================================
# ADD EMPLOYEE
# =====================================================

@login_required(login_url='login')
def add_employee(request):

    departments = Department.objects.all().order_by('name')

    if request.method == 'POST':

        Employee.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            salary=request.POST.get('salary'),
            department_id=request.POST.get('department')
        )

        return redirect('employee_list')

    return render(
        request,
        'employees/add_employee.html',
        {
            'departments': departments
        }
    )


# =====================================================
# EDIT EMPLOYEE
# =====================================================

@login_required(login_url='login')
def edit_employee(request, id):

    employee = get_object_or_404(
        Employee,
        id=id
    )

    departments = Department.objects.all().order_by('name')

    if request.method == 'POST':

        employee.name = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.phone = request.POST.get('phone')
        employee.salary = request.POST.get('salary')
        employee.department_id = request.POST.get('department')

        employee.save()

        return redirect('employee_list')

    return render(
        request,
        'employees/edit_employee.html',
        {
            'employee': employee,
            'departments': departments
        }
    )


# =====================================================
# DELETE EMPLOYEE
# =====================================================

@login_required(login_url='login')
def delete_employee(request, id):

    employee = get_object_or_404(
        Employee,
        id=id
    )

    if request.method == 'POST':

        employee.delete()

        return redirect('employee_list')

    return render(
        request,
        'employees/delete_employee.html',
        {
            'employee': employee
        }
    )


# =====================================================
# DEPARTMENT LIST
# =====================================================

@login_required(login_url='login')
def department_list(request):

    departments = Department.objects.all().order_by('-id')

    return render(
        request,
        'employees/departments.html',
        {
            'departments': departments
        }
    )


# =====================================================
# ADD DEPARTMENT
# =====================================================

@login_required(login_url='login')
def add_department(request):

    error = None

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        if not name:

            error = 'Department name cannot be empty.'

        elif Department.objects.filter(
            name__iexact=name
        ).exists():

            error = 'This department already exists.'

        else:

            Department.objects.create(
                name=name
            )

            return redirect('department_list')

    return render(
        request,
        'employees/add_department.html',
        {
            'error': error
        }
    )


# =====================================================
# EDIT DEPARTMENT
# =====================================================

@login_required(login_url='login')
def edit_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    error = None

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        if not name:

            error = 'Department name cannot be empty.'

        elif Department.objects.filter(
            name__iexact=name
        ).exclude(
            id=department.id
        ).exists():

            error = 'This department already exists.'

        else:

            department.name = name

            department.save()

            return redirect('department_list')

    return render(
        request,
        'employees/edit_department.html',
        {
            'department': department,
            'error': error
        }
    )


# =====================================================
# DELETE DEPARTMENT
# =====================================================

@login_required(login_url='login')
def delete_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    if request.method == 'POST':

        department.delete()

        return redirect('department_list')

    return render(
        request,
        'employees/delete_department.html',
        {
            'department': department
        }
    )


# =====================================================
# SALARY LIST
# =====================================================

@login_required(login_url='login')
def salary_list(request):

    employees = Employee.objects.select_related(
        'department'
    ).order_by('-salary')

    total_salary = Employee.objects.aggregate(
        Sum('salary')
    )['salary__sum'] or 0

    highest_salary = (
        employees.first().salary
        if employees.exists()
        else 0
    )

    lowest_salary = (
        employees.last().salary
        if employees.exists()
        else 0
    )

    context = {
        'employees': employees,
        'total_salary': total_salary,
        'highest_salary': highest_salary,
        'lowest_salary': lowest_salary,
    }

    return render(
        request,
        'employees/salary.html',
        context
    )


# =====================================================
# REPORTS
# =====================================================

@login_required(login_url='login')
def reports(request):

    employees = Employee.objects.select_related(
        'department'
    )

    total_employees = employees.count()

    total_departments = Department.objects.count()

    total_salary = employees.aggregate(
        total=Sum('salary')
    )['total'] or 0

    average_salary = employees.aggregate(
        average=Avg('salary')
    )['average'] or 0

    highest_salary = employees.aggregate(
        highest=Max('salary')
    )['highest'] or 0

    lowest_salary = employees.aggregate(
        lowest=Min('salary')
    )['lowest'] or 0

    department_reports = Department.objects.annotate(
        employee_count=Count('employee'),
        total_salary=Sum('employee__salary')
    ).order_by('id')

    context = {
        'employees': employees,
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_salary': total_salary,
        'average_salary': average_salary,
        'highest_salary': highest_salary,
        'lowest_salary': lowest_salary,
        'department_reports': department_reports,
    }

    return render(
        request,
        'employees/reports.html',
        context
    )


# =====================================================
# AI ASSISTANT
# English + Hindi + Hinglish
# =====================================================

@login_required(login_url='login')
def ai_assistant(request):

    # IMPORTANT:
    # Default values are required for GET request.
    # This prevents UnboundLocalError.

    question = ''
    answer = ''

    if request.method == 'POST':

        question = request.POST.get(
            'question',
            ''
        ).strip()

        question_lower = question.lower()

        employees = Employee.objects.select_related(
            'department'
        )

        # =================================================
        # TOTAL EMPLOYEES
        # =================================================

        if (
            'total employee' in question_lower
            or 'how many employee' in question_lower
            or 'number of employee' in question_lower
            or 'कितने कर्मचारी' in question
            or 'कितने employee' in question_lower
            or 'कुल कर्मचारी' in question
            or 'kitne employee' in question_lower
            or 'kitne employees' in question_lower
            or 'company mein kitne' in question_lower
            or 'company me kitne' in question_lower
        ):

            count = employees.count()

            if (
                'कितने' in question
                or 'कुल' in question
                or 'कर्मचारी' in question
            ):

                answer = (
                    f"कंपनी में कुल {count} कर्मचारी हैं।"
                )

            elif (
                'kitne' in question_lower
                or 'company mein' in question_lower
                or 'company me' in question_lower
            ):

                answer = (
                    f"Company mein total "
                    f"{count} employees hain."
                )

            else:

                answer = (
                    f"There are {count} employees "
                    f"in the company."
                )


        # =================================================
        # EMPLOYEE NAMES
        # =================================================

        elif (
            'employee names' in question_lower
            or 'list all employee' in question_lower
            or 'list employee' in question_lower
            or 'all employees' in question_lower
            or 'कर्मचारियों के नाम' in question
            or 'कर्मचारी के नाम' in question
            or 'सभी कर्मचारी' in question
            or 'employee ke naam' in question_lower
            or 'employees ke naam' in question_lower
        ):

            names = list(
                employees.values_list(
                    'name',
                    flat=True
                )
            )

            if names:

                if (
                    'कर्मचारियों' in question
                    or 'कर्मचारी' in question
                    or 'नाम' in question
                ):

                    answer = (
                        "कर्मचारियों के नाम हैं: "
                        + ", ".join(names)
                        + "।"
                    )

                elif 'ke naam' in question_lower:

                    answer = (
                        "Employees ke naam hain: "
                        + ", ".join(names)
                        + "."
                    )

                else:

                    answer = (
                        "Employees are: "
                        + ", ".join(names)
                        + "."
                    )

            else:

                answer = "No employees found."


        # =================================================
        # TOTAL SALARY
        # =================================================

        elif (
            'total salary' in question_lower
            or 'कुल सैलरी' in question
            or 'कुल वेतन' in question
            or 'salary kitni' in question_lower
            or 'total salary kitni' in question_lower
            or 'kul salary' in question_lower
            or 'kul vetan' in question_lower
        ):

            total = employees.aggregate(
                total=Sum('salary')
            )['total'] or 0

            if (
                'कुल' in question
                or 'सैलरी' in question
                or 'वेतन' in question
            ):

                answer = (
                    f"कुल सैलरी ₹{total:.2f} है।"
                )

            elif (
                'kitni' in question_lower
                or 'kul salary' in question_lower
            ):

                answer = (
                    f"Total salary ₹{total:.2f} hai."
                )

            else:

                answer = (
                    f"The total salary is "
                    f"₹{total:.2f}."
                )


        # =================================================
        # AVERAGE SALARY
        # =================================================

        elif (
            'average salary' in question_lower
            or 'औसत सैलरी' in question
            or 'औसत वेतन' in question
            or 'average salary kya' in question_lower
            or 'average salary kitni' in question_lower
            or 'avg salary' in question_lower
        ):

            average = employees.aggregate(
                average=Avg('salary')
            )['average'] or 0

            if (
                'औसत' in question
                or 'सैलरी' in question
                or 'वेतन' in question
            ):

                answer = (
                    f"औसत सैलरी ₹{average:.2f} है।"
                )

            elif (
                'kya' in question_lower
                or 'kitni' in question_lower
            ):

                answer = (
                    f"Average salary ₹{average:.2f} hai."
                )

            else:

                answer = (
                    f"The average salary is "
                    f"₹{average:.2f}."
                )


        # =================================================
        # HIGHEST SALARY
        # =================================================

        elif (
            'highest salary' in question_lower
            or 'highest paid' in question_lower
            or 'maximum salary' in question_lower
            or 'सबसे ज्यादा सैलरी' in question
            or 'सबसे अधिक सैलरी' in question
            or 'सबसे ज्यादा वेतन' in question
            or 'sabse jyada salary' in question_lower
            or 'sabse zyada salary' in question_lower
            or 'highest salary kiski' in question_lower
        ):

            employee = employees.order_by(
                '-salary'
            ).first()

            if employee:

                if (
                    'सबसे' in question
                    or 'ज्यादा' in question
                    or 'अधिक' in question
                ):

                    answer = (
                        f"{employee.name} की सैलरी सबसे "
                        f"ज्यादा है: ₹{employee.salary:.2f}।"
                    )

                elif (
                    'sabse' in question_lower
                    or 'kiski' in question_lower
                ):

                    answer = (
                        f"{employee.name} ki salary sabse "
                        f"jyada hai: ₹{employee.salary:.2f}."
                    )

                else:

                    answer = (
                        f"{employee.name} has the highest "
                        f"salary of ₹{employee.salary:.2f}."
                    )

            else:

                answer = (
                    "No employee data is available."
                )


        # =================================================
        # LOWEST SALARY
        # =================================================

        elif (
            'lowest salary' in question_lower
            or 'lowest paid' in question_lower
            or 'minimum salary' in question_lower
            or 'सबसे कम सैलरी' in question
            or 'सबसे कम वेतन' in question
            or 'sabse kam salary' in question_lower
            or 'lowest salary kiski' in question_lower
        ):

            employee = employees.order_by(
                'salary'
            ).first()

            if employee:

                if (
                    'सबसे' in question
                    or 'कम' in question
                ):

                    answer = (
                        f"{employee.name} की सैलरी सबसे कम "
                        f"है: ₹{employee.salary:.2f}।"
                    )

                elif (
                    'sabse' in question_lower
                    or 'kiski' in question_lower
                ):

                    answer = (
                        f"{employee.name} ki salary sabse "
                        f"kam hai: ₹{employee.salary:.2f}."
                    )

                else:

                    answer = (
                        f"{employee.name} has the lowest "
                        f"salary of ₹{employee.salary:.2f}."
                    )

            else:

                answer = (
                    "No employee data is available."
                )


        # =================================================
        # DEPARTMENT LIST
        # =================================================

        elif (
            'list all department' in question_lower
            or 'what departments' in question_lower
            or 'available departments' in question_lower
            or 'कौन कौन से विभाग' in question
            or 'कौन-कौन से विभाग' in question
            or 'सभी विभाग' in question
            or 'departments kaun' in question_lower
            or 'kaun se departments' in question_lower
            or 'department list' in question_lower
        ):

            department_list = list(
                Department.objects.values_list(
                    'name',
                    flat=True
                )
            )

            if department_list:

                if (
                    'विभाग' in question
                    or 'कौन' in question
                    or 'सभी' in question
                ):

                    answer = (
                        "उपलब्ध विभाग हैं: "
                        + ", ".join(department_list)
                        + "।"
                    )

                else:

                    answer = (
                        "Available departments hain: "
                        + ", ".join(department_list)
                        + "."
                    )

            else:

                answer = "No departments found."


        # =================================================
        # EMPLOYEES BY DEPARTMENT
        # =================================================

        elif (
            'who works in' in question_lower
            or 'employees in' in question_lower
            or 'employee in' in question_lower
            or 'में कौन काम करता' in question
            or 'में कौन कर्मचारी' in question
            or 'employees kaha' in question_lower
            or 'employees kahan' in question_lower
            or 'kaun kaam karta' in question_lower
        ):

            department_found = None

            departments = Department.objects.all()

            for department in departments:

                if department.name.lower() in question_lower:

                    department_found = department
                    break

            if department_found:

                dept_employees = employees.filter(
                    department=department_found
                )

                names = list(
                    dept_employees.values_list(
                        'name',
                        flat=True
                    )
                )

                if names:

                    if 'में' in question:

                        answer = (
                            f"{department_found.name} विभाग में "
                            f"काम करने वाले कर्मचारी हैं: "
                            + ", ".join(names)
                            + "।"
                        )

                    else:

                        answer = (
                            f"Employees in "
                            f"{department_found.name}: "
                            + ", ".join(names)
                            + "."
                        )

                else:

                    answer = (
                        f"No employees found in "
                        f"{department_found.name}."
                    )

            else:

                answer = (
                    "I could not find that department."
                )


        # =================================================
        # SALARY GREATER THAN AMOUNT
        # =================================================

        elif (
            'salary above' in question_lower
            or 'salary greater than' in question_lower
            or 'earning more than' in question_lower
            or 'salary more than' in question_lower
            or 'salary se jyada' in question_lower
            or 'salary se zyada' in question_lower
            or 'salary adhik' in question_lower
            or 'से ज्यादा सैलरी' in question
            or 'से अधिक सैलरी' in question
        ):

            numbers = re.findall(
                r'\d+(?:\.\d+)?',
                question
            )

            if numbers:

                amount = float(numbers[0])

                high_salary_employees = employees.filter(
                    salary__gt=amount
                )

                if high_salary_employees.exists():

                    result = []

                    for employee in high_salary_employees:

                        result.append(
                            f"{employee.name} "
                            f"(₹{employee.salary:.2f})"
                        )

                    answer = (
                        f"Employees earning more than "
                        f"₹{amount:.2f}: "
                        + ", ".join(result)
                        + "."
                    )

                else:

                    answer = (
                        f"No employees earn more than "
                        f"₹{amount:.2f}."
                    )

            else:

                answer = (
                    "Please specify a salary amount."
                )


        # =================================================
        # UNKNOWN QUESTION
        # =================================================

        else:

            answer = (
                "Sorry, I could not understand your question.\n\n"
                "You can ask about employees, departments "
                "or salaries.\n\n"
                "आप कर्मचारी, विभाग या सैलरी से संबंधित "
                "सवाल पूछ सकते हैं।"
            )


    # =====================================================
    # QUESTION + ANSWER
    # =====================================================

    context = {
        'question': question,
        'answer': answer,
    }

    return render(
        request,
        'employees/ai_assistant.html',
        context
    )