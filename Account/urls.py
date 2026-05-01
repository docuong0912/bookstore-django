from django.urls import path
from . import views

urlpatterns = [
    # API Đăng ký tài khoản mới
    path('register/', views.register, name='register'),
    
    # API Đăng nhập
    path('login/', views.user_login, name='login'),
]