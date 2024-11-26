from .models import Employee, WorkLog, Leave
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework import serializers
from datetime import datetime, time


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user_type = self.context.get('user_type')

        if not Employee.objects.filter(username=data['username'], role=user_type).exists():
            raise ValidationError(f"User must be either {user_type}")

        # validate username and password
        user = authenticate(username=data['username'],
                            password=data['password'])

        if not user:
            raise ValidationError("Invalid credentials")

        # extra validations: user must be active or staff/manager
        if not user.is_active:
            raise ValidationError("User account is not active")

        return {'user': user}


class WorkLogSerializer(serializers.ModelSerializer):
    employee_username = serializers.CharField(source='employee.username', read_only=True)
    late_minutes = serializers.SerializerMethodField()  # to calculate late minutes

    class Meta:
        model = WorkLog
        fields = [
            'id',
            'employee',
            'employee_username',
            'check_in',
            'check_out',
            'date',
            'late_minutes',  # late period
        ]
        read_only_fields = ['employee_username', 'late_minutes']  # only readable late minutes and employee username

    def get_late_minutes(self, obj):
        if obj.check_in:
            # work start time is 08:00
            work_start_time = datetime.combine(obj.date, time(8, 0))
            if obj.check_in > work_start_time:
                late_duration = obj.check_in - work_start_time
                return late_duration.seconds // 60  # changed to minutes
        return 0  # if is not late, return 0


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_username = serializers.CharField(source='employee.username', read_only=True)  # worker's username
    substitute_username = serializers.CharField(source='substitute.username', read_only=True)  # substitute's username

    class Meta:
        model = Leave
        fields = [
            'id',
            'employee',
            'employee_username',
            'start_date',
            'end_date',
            'created_at',
            'status',
            'description',
            'substitute_username',
        ]
        read_only_fields = ['employee_username', 'substitute_username']  # only readable employee and substitute username