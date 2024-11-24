from .models import Employee
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.core.exceptions import ValidationError


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
