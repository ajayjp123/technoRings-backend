from django.contrib import admin
from .models import Tool, Job, Machine, Performs, Breakdown,Employee2
from .resources import Employee2Resource,ToolResource,JobResource

from import_export.admin import ImportExportModelAdmin

# Register your models here.

@admin.register(Employee2)
class Employee2Admin(ImportExportModelAdmin):
    list_display = ['emp_ssn', 'emp_name', 'emp_designation', 'emp_shed', 'emp_dept','emp_efficiency']
    resource_class = Employee2Resource


@admin.register(Tool)
class ToolAdmin(ImportExportModelAdmin):
    list_display = ['tool_code', 'tool_name', 'max_life_expectancy_in_mm', 'cost', 'length_cut_so_far', 'no_of_brk_points', 'tool_efficiency']
    resource_class=ToolResource


@admin.register(Job)
class JobAdmin(ImportExportModelAdmin):
    list_display = ['part_no', 'component_name', 'depth_of_cut', 'no_of_holes','operation_no','tool_code']
    resource_class=JobResource


@admin.register(Machine)
class MachineAdmin(ImportExportModelAdmin):
    list_display = ['machine_id', 'machine_name', 'part_no', 'tool_code']
    # resource_class=MachineResource


@admin.register(Performs)
class PerformsAdmin(ImportExportModelAdmin):
    list_display = ['date', 'emp_ssn', 'part_no', 'machine_id', 'shift_number', 'shift_duration','partial_shift',  'target', 'achieved']
    # resource_class=PerformsResource


@admin.register(Breakdown)
class BreakdownAdmin(ImportExportModelAdmin):
    list_display = ['date', 'tool_code', 'machine_id', 'length_used', 'expected_length_remaining', 'replaced_by', 'reason', 'change_time', 'no_of_min_into_shift']
    # resource_class=BreakdownResource





