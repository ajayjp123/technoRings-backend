# Generated by Django 5.0.3 on 2024-03-17 02:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('tool_code', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('tool_name', models.CharField(max_length=100)),
                ('max_life_expectancy_in_mm', models.FloatField()),
                ('cost', models.FloatField()),
                ('length_cut_so_far', models.FloatField()),
                ('no_of_brk_points', models.IntegerField(default=None, null=True)),
                ('tool_efficiency', models.FloatField(default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Employee2',
            fields=[
                ('emp_ssn', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('emp_name', models.CharField(max_length=100)),
                ('emp_designation', models.CharField(max_length=10)),
                ('emp_shed', models.CharField(max_length=100)),
                ('emp_dept', models.CharField(max_length=100)),
                ('emp_efficiency', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('part_no', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('component_name', models.CharField(max_length=100)),
                ('depth_of_cut', models.FloatField()),
                ('no_of_holes', models.IntegerField()),
                ('operation_no', models.IntegerField()),
                ('tool_code', models.ForeignKey(db_column='tool_code', on_delete=django.db.models.deletion.CASCADE, to='webapp.tool')),
            ],
            options={
                'unique_together': {('part_no', 'tool_code')},
            },
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('machine_id', models.IntegerField(primary_key=True, serialize=False)),
                ('machine_name', models.CharField(max_length=100)),
                ('part_no', models.ForeignKey(db_column='part_no', on_delete=django.db.models.deletion.CASCADE, to='webapp.job')),
                ('tool_code', models.ForeignKey(db_column='tool_code', on_delete=django.db.models.deletion.CASCADE, to='webapp.tool')),
            ],
            options={
                'unique_together': {('machine_id', 'tool_code')},
            },
        ),
        migrations.CreateModel(
            name='Breakdown',
            fields=[
                ('date', models.DateField()),
                ('tool_code', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='breakdown_reverse', serialize=False, to='webapp.tool')),
                ('length_used', models.FloatField()),
                ('expected_length_remaining', models.FloatField()),
                ('reason', models.CharField(max_length=100)),
                ('change_time', models.DurationField()),
                ('no_of_min_into_shift', models.IntegerField()),
                ('machine_id', models.ForeignKey(db_column='machine_id', on_delete=django.db.models.deletion.CASCADE, to='webapp.machine')),
                ('replaced_by', models.ForeignKey(db_column='replaced_by', on_delete=django.db.models.deletion.CASCADE, to='webapp.tool')),
            ],
        ),
        migrations.CreateModel(
            name='Performs',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('shift_number', models.IntegerField()),
                ('shift_duration', models.FloatField()),
                ('partial_shift', models.IntegerField()),
                ('target', models.IntegerField()),
                ('achieved', models.IntegerField()),
                ('emp_ssn', models.ForeignKey(db_column='emp_ssn', on_delete=django.db.models.deletion.CASCADE, to='webapp.employee2')),
                ('machine_id', models.ForeignKey(db_column='machine_id', on_delete=django.db.models.deletion.CASCADE, to='webapp.machine')),
                ('part_no', models.ForeignKey(db_column='part_no', on_delete=django.db.models.deletion.CASCADE, to='webapp.job')),
            ],
            options={
                'ordering': ['date', 'emp_ssn', 'part_no', 'machine_id', 'shift_number', 'shift_duration', 'partial_shift', 'target', 'achieved'],
                'unique_together': {('date', 'emp_ssn', 'part_no')},
            },
        ),
    ]