from django.urls import path

from . import views
urlpatterns = [
    # API schema and documentation
    path('provinces/', views.get_all_provinces, name='get_all_provinces'),
    path('wards/<int:province_code>/', views.get_wards_by_province, name='get_wards_by_province'),
]