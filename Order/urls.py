from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('history/', views.get_order_history, name='order_history'),
    path('details/<int:order_id>/', views.get_order_details, name='get_order_details'),
]