from django.shortcuts import render
import logging
from django.http import JsonResponse, HttpResponse
import requests
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import api_view

logger = logging.getLogger(__name__)
# Create your views here.
@extend_schema(
    summary="Get All Provinces",
    description="Retrieve a list of all provinces.",
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(["GET"])
def get_all_provinces(request):
    # Simulate fetching provinces from the database
    cached_provinces_key = "all_provinces"
    all_provinces = cache.get(cached_provinces_key)
    try:
        province_data=[]
        if all_provinces is not None:
            province_data = [
                {
                    "name": province["name"],
                    "code": province["code"],
                }
                for province in all_provinces
            ]
            return JsonResponse(province_data, safe=False)
        provinces = requests.get('https://provinces.open-api.vn/api/v2/p/')
        cache.set(cached_provinces_key, provinces.json(), timeout=60*60)  # Cache for 1 hour
        province_data = [
            {
                "name": province["name"],
                "code": province["code"],
            }
            for province in provinces.json()
        ]
        return JsonResponse(province_data, safe=False)
    except Exception as e:
        logger.error(f"Error fetching provinces: {e}")
        return JsonResponse({'error': 'Failed to fetch provinces'}, status=500)
    
@extend_schema(
    summary="Get Districts by Province",
    description="Retrieve a list of districts based on the provided province code.",
    parameters=[
        OpenApiParameter("province_code", location=OpenApiParameter.PATH, type=OpenApiTypes.STR, description="The code of the province to fetch districts for")
    ],
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(["GET"])    
def get_wards_by_province(request, province_code):
    # Simulate fetching wards based on province code
    cached_wards_key = f"wards_{province_code}"
    wards = cache.get(cached_wards_key)
    
    try:
        wards_data = []
        if wards is not None:
            wards_data = [
                {
                    "name": ward["name"],
                    "code": ward["code"],
                }
                for ward in wards
            ]
            return JsonResponse(wards_data, safe=False)
        wards_response = requests.get(f'https://provinces.open-api.vn/api/v2/w?province={province_code}')
        cache.set(cached_wards_key, wards_response.json(), timeout=60*60)  # Cache for 1 hour
        wards_data = [
            {
                "name": ward["name"],
                "code": ward["code"],
            }
            for ward in wards_response.json()
        ]
        return JsonResponse(wards_data, safe=False)
    except Exception as e:
        logger.error(f"Error fetching wards for province {province_code}: {e}")
        return JsonResponse({'error': 'Failed to fetch wards'}, status=500)


