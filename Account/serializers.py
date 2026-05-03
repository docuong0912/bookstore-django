import re
from django.contrib.auth import authenticate
from rest_framework import serializers
from Account.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone', 'address']
        extra_kwargs = {
            # Các thông tin bên dưới chỉ nhận vào, không hiện ra JSON trả về
            'password': {'write_only': True},
            'email': {'write_only': True},
            'phone': {'write_only': True},
            'address': {'write_only': True},
        }

    def validate_username(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Username must be at least 5 characters.")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        return value
    
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value
    
    def validate_phone(self, value):
        clean_value = value.strip()
        if clean_value and not re.match(r'^\d{10,11}$', clean_value):
            raise serializers.ValidationError("Phone number must be 10 to 11 digits.")
        return value
    
    def validate_address(self, value):
        if value and len(value) < 10:
            raise serializers.ValidationError("Address is too short. Please provide a detailed address.")
        return value
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user
        return data
    