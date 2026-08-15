from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required

import re

from .models import Employee, Department


# ============================================================
# DASHBOARD
# ============================================================

@login_required(login_url='login')
def dashboard(request):

    total_employees = Employee.objects.count()

    total_departments = Department.objects.count()

    total_salary = (
        Employee.objects.aggregate(
            total=Sum('salary')
        )['total'] or 0
    )

    recent_employees = (
        Employee.objects
        .select_related('department')
        .order_by('-id')[:5]
    )

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


# ============================================================
# EMPLOYEE LIST
# ============================================================

@login_required(login_url='login')
def employee_list(request):

    employees = (
        Employee.objects
        .select_related('department')
        .order_by('-id')
    )

    return render(
        request,
        'employees/employees.html',
        {
            'employees': employees
        }
    )


# ============================================================
# ADD EMPLOYEE
# ============================================================

@login_required(login_url='login')
def add_employee(request):

    departments = Department.objects.all()

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


# ============================================================
# EDIT EMPLOYEE
# ============================================================

@login_required(login_url='login')
def edit_employee(request, id):

    employee = get_object_or_404(
        Employee,
        id=id
    )

    departments = Department.objects.all()

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


# ============================================================
# DELETE EMPLOYEE
# ============================================================

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


# ============================================================
# DEPARTMENT LIST
# ============================================================

@login_required(login_url='login')
def department_list(request):

    departments = (
        Department.objects
        .all()
        .order_by('-id')
    )

    return render(
        request,
        'employees/departments.html',
        {
            'departments': departments
        }
    )


# ============================================================
# ADD DEPARTMENT
# ============================================================

@login_required(login_url='login')
def add_department(request):

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()

        if name:

            existing = Department.objects.filter(
                name__iexact=name
            ).exists()

            if not existing:

                Department.objects.create(
                    name=name
                )

        return redirect('department_list')

    return render(
        request,
        'employees/add_department.html'
    )


# ============================================================
# EDIT DEPARTMENT
# ============================================================

@login_required(login_url='login')
def edit_department(request, id):

    department = get_object_or_404(
        Department,
        id=id
    )

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        if name:

            department.name = name
            department.save()

        return redirect('department_list')

    return render(
        request,
        'employees/edit_department.html',
        {
            'department': department
        }
    )


# ============================================================
# DELETE DEPARTMENT
# ============================================================

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


# ============================================================
# SALARY LIST
# ============================================================

@login_required(login_url='login')
def salary_list(request):

    employees = (
        Employee.objects
        .select_related('department')
        .order_by('-salary')
    )

    total_salary = (
        Employee.objects.aggregate(
            total=Sum('salary')
        )['total'] or 0
    )

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


# ============================================================
# AI ASSISTANT
# ============================================================

@login_required(login_url='login')
def ai_assistant(request):

    question = ''
    answer = ''

    if request.method == 'POST':

        question = request.POST.get(
            'question',
            ''
        ).strip()

        question_lower = question.lower()

        employees = (
            Employee.objects
            .select_related('department')
            .all()
        )

        # ====================================================
        # EMPTY QUESTION
        # ====================================================

        if not question:

            answer = (
                "Please enter a question. "
                "आप अपना सवाल लिखिए।"
            )

        # ====================================================
        # 1. EMPLOYEE-SPECIFIC SALARY
        # ====================================================

        else:

            matched_employee = None

            for employee in employees:

                full_name = (
                    employee.name
                    or ''
                ).strip()

                full_name_lower = full_name.lower()

                name_parts = full_name_lower.split()

                if not name_parts:
                    continue

                first_name = name_parts[0]

                # Full name match
                if full_name_lower in question_lower:

                    matched_employee = employee
                    break

                # First name match
                if re.search(
                    r'\b' + re.escape(first_name) + r'\b',
                    question_lower
                ):

                    matched_employee = employee
                    break

            # ====================================================
            # SALARY QUESTION
            # ====================================================

            salary_words = [
                'salary',
                'salaries',
                'pay',
                'wage',
                'वेतन',
                'सैलरी',
                'तनख्वाह'
            ]

            is_salary_question = any(
                word in question_lower
                for word in salary_words
            ) or any(
                word in question
                for word in [
                    'वेतन',
                    'सैलरी',
                    'तनख्वाह'
                ]
            )

            # ====================================================
            # 2. EMPLOYEE SPECIFIC SALARY
            # ====================================================

            if matched_employee and is_salary_question:

                salary = matched_employee.salary

                if (
                    'है' in question
                    or 'कितनी' in question
                    or 'क्या' in question
                    or 'वेतन' in question
                    or 'सैलरी' in question
                ):

                    answer = (
                        f"{matched_employee.name} की सैलरी "
                        f"₹{salary:.2f} है।"
                    )

                elif (
                    'ki' in question_lower
                    or 'kitni' in question_lower
                    or 'kya' in question_lower
                ):

                    answer = (
                        f"{matched_employee.name} ki salary "
                        f"₹{salary:.2f} hai."
                    )

                else:

                    answer = (
                        f"{matched_employee.name}'s salary is "
                        f"₹{salary:.2f}."
                    )

            # ====================================================
            # 3. TOTAL SALARY
            # ====================================================

            elif (
                'total salary' in question_lower
                or 'total salaries' in question_lower
                or 'salary total' in question_lower
                or 'total pay' in question_lower
                or 'कुल सैलरी' in question
                or 'कुल वेतन' in question
                or 'कुल तनख्वाह' in question
                or 'kul salary' in question_lower
                or 'kul salaries' in question_lower
            ):

                total = (
                    employees.aggregate(
                        total=Sum('salary')
                    )['total'] or 0
                )

                if (
                    'कुल' in question
                    or 'वेतन' in question
                    or 'सैलरी' in question
                ):

                    answer = (
                        f"कुल सैलरी ₹{total:.2f} है।"
                    )

                elif (
                    'kul' in question_lower
                    or 'hai' in question_lower
                ):

                    answer = (
                        f"Total salary ₹{total:.2f} hai."
                    )

                else:

                    answer = (
                        f"The total salary is ₹{total:.2f}."
                    )

            # ====================================================
            # 4. TOTAL EMPLOYEES
            # ====================================================

            elif (
                'how many employees' in question_lower
                or 'how many employee' in question_lower
                or 'number of employees' in question_lower
                or 'number of employee' in question_lower
                or 'total employees' in question_lower
                or 'total employee' in question_lower
                or 'employee count' in question_lower
                or 'कितने कर्मचारी' in question
                or 'कुल कर्मचारी' in question
                or 'kitne employees' in question_lower
                or 'kitne employee' in question_lower
                or 'kitne employees hain' in question_lower
                or 'kitne employee hain' in question_lower
            ):

                count = employees.count()

                if (
                    'कितने' in question
                    or 'कुल कर्मचारी' in question
                ):

                    answer = (
                        f"कंपनी में कुल {count} कर्मचारी हैं।"
                    )

                elif 'kitne' in question_lower:

                    answer = (
                        f"Company mein total "
                        f"{count} employees hain."
                    )

                else:

                    answer = (
                        f"There are {count} employees "
                        f"in the company."
                    )

            # ====================================================
            # 5. EMPLOYEE NAMES
            # ====================================================

            elif (
                'employee names' in question_lower
                or 'employees names' in question_lower
                or 'list employee names' in question_lower
                or 'list of employee names' in question_lower
                or 'list all employee names' in question_lower
                or 'who are the employees' in question_lower
                or 'employee name' in question_lower
                or 'employee ke naam' in question_lower
                or 'employees ke naam' in question_lower
                or 'karmchari ke naam' in question_lower
                or 'कर्मचारियों के नाम' in question
                or 'कर्मचारी के नाम' in question
                or 'सभी कर्मचारियों के नाम' in question
            ):

                names = list(
                    employees.values_list(
                        'name',
                        flat=True
                    )
                )

                if names:

                    if (
                        'कर्मचारी' in question
                        or 'नाम' in question
                    ):

                        answer = (
                            "कर्मचारियों के नाम हैं: "
                            + ", ".join(names)
                            + "।"
                        )

                    elif (
                        'ke naam' in question_lower
                        or 'naam' in question_lower
                    ):

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

            # ====================================================
            # 6. AVERAGE SALARY
            # ====================================================

            elif (
                'average salary' in question_lower
                or 'avg salary' in question_lower
                or 'average salaries' in question_lower
                or 'औसत सैलरी' in question
                or 'औसत वेतन' in question
                or 'average salary kitni' in question_lower
                or 'average salary kya' in question_lower
            ):

                average = (
                    employees.aggregate(
                        average=Avg('salary')
                    )['average'] or 0
                )

                if 'औसत' in question:

                    answer = (
                        f"औसत सैलरी ₹{average:.2f} है।"
                    )

                elif (
                    'kitni' in question_lower
                    or 'kya' in question_lower
                ):

                    answer = (
                        f"Average salary ₹{average:.2f} hai."
                    )

                else:

                    answer = (
                        f"The average salary is "
                        f"₹{average:.2f}."
                    )

            # ====================================================
            # 7. HIGHEST SALARY
            # ====================================================

            elif (
                'highest salary' in question_lower
                or 'maximum salary' in question_lower
                or 'highest paid' in question_lower
                or 'highest salary employee' in question_lower
                or 'who has the highest salary' in question_lower
                or 'highest paid employee' in question_lower
                or 'सबसे ज्यादा सैलरी' in question
                or 'सबसे अधिक सैलरी' in question
                or 'सबसे ज्यादा वेतन' in question
                or 'सबसे अधिक वेतन' in question
                or 'sabse jyada salary' in question_lower
                or 'sabse zyada salary' in question_lower
                or 'sabse jyada salary kiski' in question_lower
                or 'highest salary kiski' in question_lower
            ):

                employee = (
                    employees
                    .order_by('-salary')
                    .first()
                )

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

            # ====================================================
            # 8. LOWEST SALARY
            # ====================================================

            elif (
                'lowest salary' in question_lower
                or 'minimum salary' in question_lower
                or 'lowest paid' in question_lower
                or 'lowest salary employee' in question_lower
                or 'who has the lowest salary' in question_lower
                or 'सबसे कम सैलरी' in question
                or 'सबसे कम वेतन' in question
                or 'sabse kam salary' in question_lower
                or 'lowest salary kiski' in question_lower
                or 'sabse kam salary kiski' in question_lower
            ):

                employee = (
                    employees
                    .order_by('salary')
                    .first()
                )

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

            # ====================================================
            # 9. DEPARTMENT LIST
            # ====================================================

            elif (
                'department list' in question_lower
                or 'list departments' in question_lower
                or 'list all departments' in question_lower
                or 'what departments' in question_lower
                or 'available departments' in question_lower
                or 'which departments' in question_lower
                or 'departments kaun' in question_lower
                or 'kaun se departments' in question_lower
                or 'kaun kaun se departments' in question_lower
                or 'सभी विभाग' in question
                or 'कौन से विभाग' in question
                or 'कौन कौन से विभाग' in question
                or 'कौन-कौन से विभाग' in question
            ):

                departments = list(
                    Department.objects.values_list(
                        'name',
                        flat=True
                    )
                )

                if departments:

                    if 'विभाग' in question:

                        answer = (
                            "उपलब्ध विभाग हैं: "
                            + ", ".join(departments)
                            + "।"
                        )

                    elif (
                        'kaun' in question_lower
                        or 'department' in question_lower
                    ):

                        answer = (
                            "Available departments are: "
                            + ", ".join(departments)
                            + "."
                        )

                    else:

                        answer = (
                            "Available departments are: "
                            + ", ".join(departments)
                            + "."
                        )

                else:

                    answer = "No departments found."

            # ====================================================
            # 10. EMPLOYEES BY DEPARTMENT
            # ====================================================

            elif (
                'who works in' in question_lower
                or 'employees in' in question_lower
                or 'employee in' in question_lower
                or 'employees working in' in question_lower
                or 'employee working in' in question_lower
                or 'employees kaha' in question_lower
                or 'employees kahan' in question_lower
                or 'kaun kaam karta' in question_lower
                or 'kaun kaam karte' in question_lower
                or 'में कौन काम करता' in question
                or 'में कौन कर्मचारी' in question
            ):

                found_department = None

                departments = Department.objects.all()

                for department in departments:

                    department_name = (
                        department.name
                        or ''
                    ).strip().lower()

                    if (
                        department_name
                        and department_name in question_lower
                    ):

                        found_department = department
                        break

                if found_department:

                    department_employees = (
                        employees.filter(
                            department=found_department
                        )
                    )

                    names = list(
                        department_employees.values_list(
                            'name',
                            flat=True
                        )
                    )

                    if names:

                        answer = (
                            f"Employees in "
                            f"{found_department.name}: "
                            + ", ".join(names)
                            + "."
                        )

                    else:

                        answer = (
                            f"No employees found in "
                            f"{found_department.name}."
                        )

                else:

                    answer = (
                        "I could not find that department."
                    )

            # ====================================================
            # 11. SALARY GREATER THAN
            # ====================================================

            elif (
                'salary greater than' in question_lower
                or 'salary more than' in question_lower
                or 'salary above' in question_lower
                or 'earning more than' in question_lower
                or 'employees earning more' in question_lower
                or 'salary se jyada' in question_lower
                or 'salary se zyada' in question_lower
                or 'salary se adhik' in question_lower
                or 'से ज्यादा सैलरी' in question
                or 'से अधिक सैलरी' in question
            ):

                numbers = re.findall(
                    r'\d+(?:\.\d+)?',
                    question
                )

                if numbers:

                    amount = float(numbers[0])

                    result = employees.filter(
                        salary__gt=amount
                    )

                    if result.exists():

                        employee_data = []

                        for employee in result:

                            employee_data.append(
                                f"{employee.name} "
                                f"(₹{employee.salary:.2f})"
                            )

                        answer = (
                            f"Employees earning more than "
                            f"₹{amount:.2f}: "
                            + ", ".join(employee_data)
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

            # ====================================================
            # 12. UNKNOWN QUESTION
            # ====================================================

            else:

                answer = (
                    "Sorry, I could not understand your question.\n\n"
                    "You can ask about employees, departments "
                    "or salaries.\n\n"
                    "Examples:\n"
                    "• What is Akshat's salary?\n"
                    "• What is the total salary?\n"
                    "• How many employees are there?\n"
                    "• Who has the highest salary?\n"
                    "• What departments are available?\n"
                    "• Who works in Finance?\n"
                    "• Employees earning more than 50000?\n\n"
                    "आप कर्मचारी, विभाग या सैलरी से संबंधित "
                    "सवाल पूछ सकते हैं।"
                )

    # ============================================================
    # SEND QUESTION + ANSWER TO TEMPLATE
    # ============================================================

    context = {
        'question': question,
        'answer': answer,
    }

    return render(
        request,
        'employees/ai_assistant.html',
        context
    )

    # ============================================================
# REPORTS
# ============================================================

@login_required(login_url='login')
def reports(request):

    employees = (
        Employee.objects
        .select_related('department')
        .order_by('-salary')
    )

    total_employees = Employee.objects.count()

    total_departments = Department.objects.count()

    total_salary = (
        Employee.objects.aggregate(
            total=Sum('salary')
        )['total'] or 0
    )

    average_salary = (
        Employee.objects.aggregate(
            average=Avg('salary')
        )['average'] or 0
    )

    highest_salary_employee = (
        Employee.objects
        .order_by('-salary')
        .first()
    )

    lowest_salary_employee = (
        Employee.objects
        .order_by('salary')
        .first()
    )

    context = {
        'employees': employees,
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_salary': total_salary,
        'average_salary': average_salary,
        'highest_salary_employee': highest_salary_employee,
        'lowest_salary_employee': lowest_salary_employee,
    }

    return render(
        request,
        'employees/reports.html',
        context
    )