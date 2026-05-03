from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # API Đăng ký tài khoản mới
    path('register/', views.register, name='register'),
    
    # API Đăng nhập
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='login'),
]