# serializers.py

from rest_framework import serializers
from .models import Employee2


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee2
        fields = '__all__'
