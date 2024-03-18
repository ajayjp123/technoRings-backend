from math import sumprod
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmployeeForm, ToolForm, JobForm, MachineForm,EmployeeSSNForm,ShiftSSNForm,ToolCodeForm,EmployeeSSNDateForm,ShiftSSNDateForm
from .models import Employee2, Performs, Tool, Job, Machine,Breakdown
from rest_framework import generics
from .serializers import EmployeeSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.db.models import Sum

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from .models import Performs




def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})


@method_decorator(csrf_exempt, name='dispatch')
class EmployeeCreateView(View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        serializer = EmployeeSerializer(data=data)

        if serializer.is_valid():
            new_employee = serializer.save()
            return JsonResponse({
                'emp_ssn': new_employee.emp_ssn,
                'emp_name': new_employee.emp_name,
                'address': new_employee.address,
                'mobile': new_employee.mobile,
                'emp_efficiency': new_employee.emp_efficiency,
            })
        else:
            return JsonResponse({'error': 'Invalid form data'}, status=400)


class EmployeeList(generics.ListAPIView):
    queryset = Employee2.objects.all()
    serializer_class = EmployeeSerializer


def employee_create_view(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee_instance=form.save()
            employee_instance.emp_efficiency=0
            employee_instance.save()
            return redirect('/webapp/success_page/')
    else:
        form = EmployeeForm()

    return render(request, 'webapp/employee_form.html', {'form': form})


def tool_create_view(request):
    if request.method == 'POST':
        form = ToolForm(request.POST)
        if form.is_valid():
            tool_instance = form.save(commit=False)
            
            tool_instance.no_of_brk_points = 0
            tool_instance.tool_efficiency = 0
            tool_instance.save()
            return redirect('/webapp/success_page/')
    else:
        form = ToolForm()

    return render(request, 'webapp/tool_form.html', {'form': form})


def job_create_view(request):
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        job_name = request.POST.get('job_name')

        selected_tools = request.POST.getlist('tools')
        for tool_code in selected_tools:
            length_field = f'length_{tool_code}'
            holes_field = f'no_of_holes_{tool_code}'
            length = request.POST.get(length_field)
            no_of_holes = request.POST.get(holes_field)

            tool = get_object_or_404(Tool, tool_code=tool_code)

            # Create the Job instance with the Tool reference and save it
            job = Job.objects.create(job_id=job_id, job_name=job_name, length=length, no_of_holes=no_of_holes, tool_code=tool)
            job.save()

        return redirect('success_page')  # Replace 'success_page' with the actual URL or view name
    else:
        # Retrieve tools for displaying in the form
        tools = Tool.objects.all()

    return render(request, 'webapp/job_form.html', {'tools': tools})


def create_machine(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            machine = form.save(commit=False)
            machine.save()
            form.save_m2m()  # Save the many-to-many relationships

            return redirect('success_page')  # Replace 'success_page' with the actual URL or view name
    else:
        form = MachineForm()

    jobs = Job.objects.all()

    return render(request, 'webapp/machine_form.html', {'form': form, 'jobs': jobs})


def employee_delete_view(request, emp_ssn):
    employee = get_object_or_404(Employee2, emp_ssn=emp_ssn)

    if request.method == 'POST':
        employee.delete()
        return redirect('/webapp/success_page/')

    return render(request, 'webapp/employee_delete.html', {'employee': employee})


def tool_delete_view(request, tool_code):
    tool = get_object_or_404(Tool, tool_code=tool_code)

    if request.method == 'POST':
        tool.delete()
        return redirect('/webapp/success_page/')

    return render(request, 'webapp/tool_delete.html', {'tool': tool})


def job_delete_view(request, job_id):
    job = get_object_or_404(Job, job_id=job_id)

    if request.method == 'POST':
        job.delete()
        return redirect('/webapp/success_page/')

    return render(request, 'webapp/job_delete.html', {'job': job})


def employee_update_view(request, emp_ssn):
    employee = get_object_or_404(Employee2, emp_ssn=emp_ssn)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('/webapp/success_page/')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'webapp/employee_update.html', {'form': form})


def tool_update_view(request, tool_code):
    tool = get_object_or_404(Tool, tool_code=tool_code)

    if request.method == 'POST':
        form = ToolForm(request.POST, instance=tool)
        if form.is_valid():
            form.save()
            return redirect('/webapp/success_page/')
    else:
        form = ToolForm(instance=tool)

    return render(request, 'webapp/tool_update.html', {'form': form})


def job_update_view(request, job_id):
    job = get_object_or_404(Job, job_id=job_id)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('/webapp/success_page/')
    else:
        form = JobForm(instance=job)

    return render(request, 'webapp/job_update.html', {'form': form})


def success_page(request):
    return render(request, 'webapp/success_page.html')



def calculate_employee_efficiency(emp_ssn):
    performs_aggregated = Performs.objects.filter(emp_ssn=emp_ssn).aggregate(
        shift_duration_sum=Sum('shift_duration'),
        partial_shift_sum=Sum('partial_shift'),
        target_sum=Sum('target'),
        achieved_sum=Sum('achieved')
    )

    shift_duration_sum = performs_aggregated['shift_duration_sum']
    partial_shift_sum = performs_aggregated['partial_shift_sum']
    target_sum = performs_aggregated['target_sum']
    achieved_sum = performs_aggregated['achieved_sum']

    if shift_duration_sum and partial_shift_sum and target_sum and achieved_sum:
        x = target_sum * (partial_shift_sum / shift_duration_sum)
        efficiency = (achieved_sum / x)*100
        efficiency=round(efficiency,2)
        return efficiency
    else:
        return None

def employee_efficiency_view(request):
    efficiency = None

    if request.method == 'POST':
        form = EmployeeSSNForm(request.POST)
        if form.is_valid():
            emp_ssn = form.cleaned_data['emp_ssn']
            if emp_ssn:
                efficiency = calculate_employee_efficiency(emp_ssn)
    else:
        form = EmployeeSSNForm()

    return render(request, 'webapp/employee_efficiency_form.html', {'form': form, 'efficiency': efficiency})


def calculate_shift_efficiency(shift_number):
    performs_aggregated = Performs.objects.filter(shift_number=shift_number).aggregate(
        shift_duration_sum=Sum('shift_duration'),
        partial_shift_sum=Sum('partial_shift'),
        target_sum=Sum('target'),
        achieved_sum=Sum('achieved')
    )

    shift_duration_sum = performs_aggregated['shift_duration_sum']
    partial_shift_sum = performs_aggregated['partial_shift_sum']
    target_sum = performs_aggregated['target_sum']
    achieved_sum = performs_aggregated['achieved_sum']

    if shift_duration_sum and partial_shift_sum and target_sum and achieved_sum:
        x = target_sum * (partial_shift_sum / shift_duration_sum)
        efficiency = (achieved_sum / x)*100
        efficiency=round(efficiency,2)
        return efficiency
    else:
        return None

def shift_efficiency_view(request):
    efficiency = None

    if request.method == 'POST':
        form = ShiftSSNForm(request.POST)
        if form.is_valid():
            shift_number = form.cleaned_data['shift_number']
            if shift_number:
                efficiency = calculate_shift_efficiency(shift_number)
    else:
        form = ShiftSSNForm()

    return render(request, 'webapp/shift_efficiency_form.html', {'form': form, 'efficiency': efficiency})

def breakdown_view(request):
    breakdown_data = Breakdown.objects.all()  
    return render(request, 'webapp/breakdown_form.html', {'breakdown_data': breakdown_data})






def calculate_tool_efficiency(tool_code):
    try:
        
        tool = Tool.objects.get(tool_code=tool_code)
        max_life_expectancy_in_mm = tool.max_life_expectancy_in_mm
        length_cut_so_far = tool.length_cut_so_far
        no_of_brk_points = tool.no_of_brk_points

        if max_life_expectancy_in_mm> 0 and no_of_brk_points >= 0:

            tool_life_lost = (no_of_brk_points + 1) * max_life_expectancy_in_mm
            
            efficiency = (length_cut_so_far / (length_cut_so_far + tool_life_lost)) * 100
            
            efficiency = round(efficiency, 2)
            
            return efficiency
    except Tool.DoesNotExist:
        pass
    
    return None


def tool_efficiency_view(request):
    efficiency = None

    if request.method == 'POST':
        form = ToolCodeForm(request.POST)
        if form.is_valid():
            tool_code = form.cleaned_data['tool_code']
            if tool_code:
                efficiency = calculate_tool_efficiency(tool_code)
    else:
        form = ToolCodeForm()

    return render(request, 'webapp/tool_efficiency_form.html', {'form': form, 'efficiency': efficiency})


def calculate_employee_efficiency_date(emp_ssn, start_date, end_date):
    performs_aggregated = Performs.objects.filter(
        emp_ssn=emp_ssn,
        date__range=[start_date, end_date]
    ).aggregate(
        shift_duration_sum=Sum('shift_duration'),
        partial_shift_sum=Sum('partial_shift'),
        target_sum=Sum('target'),
        achieved_sum=Sum('achieved')
    )

    shift_duration_sum = performs_aggregated['shift_duration_sum']
    partial_shift_sum = performs_aggregated['partial_shift_sum']
    target_sum = performs_aggregated['target_sum']
    achieved_sum = performs_aggregated['achieved_sum']

    if shift_duration_sum and partial_shift_sum and target_sum and achieved_sum:
        x = target_sum * (partial_shift_sum / shift_duration_sum)
        efficiency = (achieved_sum / x) * 100
        efficiency = round(efficiency, 2)
        return efficiency
    else:
        return None

def employee_efficiency_view_date(request):
    efficiency = None

    if request.method == 'POST':
        form = EmployeeSSNDateForm(request.POST)
        if form.is_valid():
            emp_ssn = form.cleaned_data['emp_ssn']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            if emp_ssn and start_date and end_date:
                efficiency = calculate_employee_efficiency_date(emp_ssn, start_date, end_date)
    else:
        form = EmployeeSSNDateForm()

    return render(request, 'webapp/employee_efficiency_form_date.html', {'form': form, 'efficiency': efficiency})

def calculate_shift_efficiency_date(shift_number, start_date, end_date):
    performs_aggregated = Performs.objects.filter(
        shift_number=shift_number,
        date__range=[start_date, end_date]
    ).aggregate(
        shift_duration_sum=Sum('shift_duration'),
        partial_shift_sum=Sum('partial_shift'),
        target_sum=Sum('target'),
        achieved_sum=Sum('achieved')
    )

    shift_duration_sum = performs_aggregated['shift_duration_sum']
    partial_shift_sum = performs_aggregated['partial_shift_sum']
    target_sum = performs_aggregated['target_sum']
    achieved_sum = performs_aggregated['achieved_sum']

    if shift_duration_sum and partial_shift_sum and target_sum and achieved_sum:
        x = target_sum * (partial_shift_sum / shift_duration_sum)
        efficiency = (achieved_sum / x) * 100
        efficiency = round(efficiency, 2)
        return efficiency
    else:
        return None

def shift_efficiency_view_date(request):
    efficiency = None

    if request.method == 'POST':
        form = ShiftSSNDateForm(request.POST)
        if form.is_valid():
            shift_number = form.cleaned_data['shift_number']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            if shift_number and start_date and end_date:
                efficiency = calculate_shift_efficiency_date(shift_number, start_date, end_date)
    else:
        form = ShiftSSNDateForm()

    return render(request, 'webapp/shift_efficiency_form_date.html', {'form': form, 'efficiency': efficiency})