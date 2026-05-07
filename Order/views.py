import logging
from django.db import DatabaseError, transaction
from django.http import JsonResponse
from django.db.models import F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from Cart.models import Cart
from Order.models import Order, OrderHistory, OrderItem
from Order.serializer import OrderSerializer
logger = logging.getLogger(__name__)

@extend_schema(
    summary="Create Order",
    description="Create a new order with the provided cart items and user information. The endpoint validates the stock availability of the books in the cart and creates an order along with order items. It also updates the stock quantity of the books accordingly.",
    request=OrderSerializer,
    responses={201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT, 500: OpenApiTypes.OBJECT},
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# Create your views here.
def create_order(request):
    # Logic to create an order
    order_serializer = OrderSerializer(data=request.data)
    try:
        if not order_serializer.is_valid():
            return JsonResponse({"error": order_serializer.errors}, status=400)
        province_id = request.data.get('province_id')
        ward_id = request.data.get('ward_id')
        # Validate province and ward IDs
        if not province_id or not ward_id:
            return JsonResponse({"error": "Province and Ward IDs are required."}, status=400)
        # Additional logic to create the order
        with transaction.atomic():
            # Create order and order items
            # ...
            cart = Cart.objects.get(id=request.data.get('cart_id'))
            
            order = Order.objects.create(
                user=request.user,
                order_name=request.data.get('order_name'),
                address=request.data.get('address'),
                email=request.data.get('email'),
                phone_number=request.data.get('phone_number'),
                province=province_id,
                ward=ward_id,
                total_quantity=cart.total_quantity,
                total_price=cart.total_price,
                delivery_fee=20000, #test
                created_by=request.user.username
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    book_title=item.book.title,
                    book_price=item.book.price,
                    quantity=item.quantity,
                    total_price=item.book.price * item.quantity
                )
                item.book.update(stock_quantity=F('stock_quantity') - item.quantity)
            
            orderHistory = OrderHistory.objects.create(
                order=order,
                note= request.data.get('note', ''),
                created_by=request.user.username
            )
            return JsonResponse({"message": "Order created successfully."}, status=201)
    except Exception as e:
        logger.error(f"Error occurred while creating order: {str(e)}")
        return JsonResponse({"error": "An error occurred while creating the order: " + str(e)}, status=500)

@extend_schema(
    summary="Get Order History",
    description="Retrieve the order history for the authenticated user. The endpoint returns a list of orders along with their details, including the items in each order. The orders are sorted by creation date in descending order.",
    responses={200: OpenApiTypes.OBJECT, 500: OpenApiTypes.OBJECT},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_history(request):
    # Logic to retrieve order history for the authenticated user
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        order_history = []
        for order in orders:
            items = order.items.all()
            order_history.append({
                "order_id": order.id,
                "order_name": order.order_name,
                "total_price": order.total_price,
                "created_at": order.created_at,
                "items": [
                    {
                        "book_title": item.book_title,
                        "quantity": item.quantity,
                        "total_price": item.total_price
                    } for item in items
                ]
            })
        return JsonResponse({"order_history": order_history}, status=200)
    except DatabaseError as e:
        logger.error(f"Database error occurred while retrieving order history: {str(e)}")
        return JsonResponse({"error": "An error occurred while retrieving the order history: " + str(e)}, status=500)

@extend_schema(
    summary="Get Order Details",
    description="Retrieve the details for a specific order.",
    responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT, 500: OpenApiTypes.OBJECT},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, order_id):
    # Logic to retrieve order details for a specific order
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        items = order.items.all()
        order_details = {
            "order_id": order.id,
            "order_name": order.order_name,
            "total_price": order.total_price,
            "created_at": order.created_at,
            "items": [
                {
                    "book_title": item.book_title,
                    "quantity": item.quantity,
                    "total_price": item.total_price
                } for item in items
            ]
        }
        return JsonResponse({"order_details": order_details}, status=200)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found."}, status=404)
    except DatabaseError as e:
        logger.error(f"Database error occurred while retrieving order details: {str(e)}")
        return JsonResponse({"error": "An error occurred while retrieving the order details: " + str(e)}, status=500)
    