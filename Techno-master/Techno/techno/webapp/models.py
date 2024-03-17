from django.db import models

class Employee2(models.Model):
    emp_ssn = models.CharField(primary_key=True, max_length=100)
    emp_name = models.CharField(max_length=100)
    emp_designation = models.CharField(max_length=10)
    emp_shed = models.CharField(max_length=100)
    emp_dept = models.CharField(max_length=100)
    emp_efficiency = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Details Of {self.emp_ssn}"

class Tool(models.Model):
    tool_code = models.CharField(primary_key=True, max_length=100)
    tool_name = models.CharField(max_length=100)
    max_life_expectancy_in_mm = models.FloatField()
    cost = models.FloatField()
    length_cut_so_far = models.FloatField()
    no_of_brk_points = models.IntegerField(default=None, null=True)
    tool_efficiency = models.FloatField(default=None, null=True)



class Job(models.Model):
    part_no= models.CharField(primary_key=True, max_length=100)  
    component_name = models.CharField(max_length=100)
    depth_of_cut = models.FloatField()
    no_of_holes = models.IntegerField()
    operation_no=models.IntegerField()
    tool_code = models.ForeignKey(Tool, on_delete=models.CASCADE, db_column='tool_code', to_field='tool_code')
    

    class Meta:
        unique_together=('part_no', 'tool_code')

    def __str__(self):
        return f"Job: {self.component_name} (ID: {self.part_no}, Tool Code: {self.tool_code})"

class Machine(models.Model):
    machine_id = models.IntegerField(primary_key=True)
    machine_name = models.CharField(max_length=100)
    part_no= models.ForeignKey(Job, on_delete=models.CASCADE, db_column='part_no', to_field='part_no')
    tool_code = models.ForeignKey(Tool, on_delete=models.CASCADE, db_column='tool_code', to_field='tool_code')

    class Meta:
        unique_together = ('machine_id', 'tool_code')

    def __str__(self):
        return f"Machine: {self.machine_name} (ID: {self.machine_id})"

class Performs(models.Model):
    date = models.DateField(primary_key=True)
    emp_ssn = models.ForeignKey(Employee2, on_delete=models.CASCADE, db_column='emp_ssn', to_field='emp_ssn')
    part_no = models.ForeignKey(Job, on_delete=models.CASCADE, db_column='part_no', to_field='part_no')
    machine_id = models.ForeignKey(Machine, on_delete=models.CASCADE, db_column='machine_id', to_field='machine_id')
    shift_number = models.IntegerField()
    shift_duration = models.FloatField()
    partial_shift = models.IntegerField()
    target = models.IntegerField()
    achieved = models.IntegerField()

    class Meta:
        ordering=['date','emp_ssn','part_no','machine_id','shift_number','shift_duration','partial_shift','target','achieved']
        unique_together = ['date', 'emp_ssn', 'part_no']

    def __str__(self):
        return f"Performs on {self.date} for {self.emp_ssn} (Job: {self.part_no.component_name}, Machine: {self.machine_id.machine_name})"

class Breakdown(models.Model):
    date = models.DateField()
    tool_code = models.OneToOneField(
        Tool,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='breakdown_reverse',
        to_field='tool_code'
    )
    machine_id = models.ForeignKey(Machine, on_delete=models.CASCADE, db_column='machine_id', to_field='machine_id')
    length_used = models.FloatField()
    expected_length_remaining = models.FloatField()
    replaced_by = models.ForeignKey(Tool, on_delete=models.CASCADE, db_column='replaced_by', to_field='tool_code')
    reason = models.CharField(max_length=100)
    change_time = models.DurationField()
    no_of_min_into_shift = models.IntegerField()

    def __str__(self):
        return f"Breakdown on {self.date} for Tool: {self.tool_code.tool_code} on Machine: {self.machine_id.machine_name}"
