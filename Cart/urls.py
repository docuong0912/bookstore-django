from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_cart_details, name='get_cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]