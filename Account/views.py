from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes
from .serializers import LoginSerializer, UserSerializer
from .models import User

# ============ 1. User Registration ============
@extend_schema(
    summary="Register new user",
    description="Create a new customer account with phone and address.",
    request=UserSerializer,
    responses={201: OpenApiTypes.OBJECT},
)
@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        User.objects.create_user(**serializer.validated_data)
        return JsonResponse({"message": "User registered successfully!"}, status=201)
    return JsonResponse(serializer.errors, status=400)

# ============ 2. User Login ============
@extend_schema(
    summary="User Login",
    description="Authenticate user and return admin status.",
    request=LoginSerializer,
    responses={200: OpenApiTypes.OBJECT},
)
@csrf_exempt
@api_view(['POST'])
def user_login(request):
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return JsonResponse({
                "message": "Login successful!",
                "is_admin": user.is_staff,
                "username": user.username
            })
        return JsonResponse(serializer.errors, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

