from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from .models import Cart, CartItem
from Book.models import Book

# ============ Get Cart Detail  ============
@extend_schema(
    summary="Get user'cart details",
    description="Retrieve all items currently in the authenticated user's cart.",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart_details(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('book').all()

    cart_items = [
        {
            "id": item.id,
            "book_isbn": item.book.isbn,
            "title": item.book.title,
            "price": float(item.book.price),
            "quantity": item.quantity,
            "subtotal": float(item.book.price * item.quantity),
            "thumbnail": item.book.thumbnail if hasattr(item.book, 'thumbnail') else None
        }
        for item in items
    ]

    total_price = sum(item['subtotal'] for item in cart_items)

    return JsonResponse({
        "items": cart_items,
        "total_price": total_price
    }, status=200)

# ============ Add Book to Cart ============
@extend_schema(
    summary="Add book to cart",
    description="Add a book to the cart using its ISBN. If the book is already in the cart, increment the quantity.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "isbn": {"type": "string"},
                "quantity": {"type": "integer", "default": 1}
            },
            "required": ["isbn"]
        }
    },
    responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    isbn = request.data.get('isbn')
    quantity = int(request.data.get('quantity', 1))

    try:
        book = Book.objects.get(isbn=isbn)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, book=book)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        return JsonResponse({"message": "Successfully added to cart"}, status=200)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)
    
# ============ Remove Item from Cart ============
@extend_schema(
    summary="Remove item from cart",
    description="Delete a specific item line from the user's cart by its ID.",
    responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        item.delete()
        return JsonResponse({"message": "item removed from cart"}, status=200)
    except CartItem.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)