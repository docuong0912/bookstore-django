from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Book, Category
import json
from django.views.decorators.http import require_http_methods
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.

# ============ List Books ============
@extend_schema(
    summary="List Books",
    description="Retrieve a list of all books with optional search and filtering parameters. Filters include price range, published date, title search, publisher, status, and author.",
    parameters=[
        OpenApiParameter("categoryId",location=OpenApiParameter.QUERY, type=OpenApiTypes.INT, description="Search books by category"),
        OpenApiParameter("title",location=OpenApiParameter.QUERY, description="Search books by title"),
        OpenApiParameter("author", location=OpenApiParameter.QUERY,  description="Filter books by author name"),
        OpenApiParameter("publisher", location=OpenApiParameter.QUERY,  description="Filter books by publisher name"),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Filter books by status (available, out_of_stock, discontinued)"),
        OpenApiParameter("min_price", location=OpenApiParameter.QUERY, description="Minimum price for filtering"),
        OpenApiParameter("max_price", location=OpenApiParameter.QUERY, description="Maximum price for filtering"),
        OpenApiParameter("start_date", location=OpenApiParameter.QUERY, type=OpenApiTypes.DATE, description="Filter books published after this date"),
        OpenApiParameter("end_date", location=OpenApiParameter.QUERY, type=OpenApiTypes.DATE, description="Filter books published before this date"),
        OpenApiParameter("page", location=OpenApiParameter.QUERY, type=OpenApiTypes.INT, description="Page number for pagination"),
        OpenApiParameter("page_size", location=OpenApiParameter.QUERY, type=OpenApiTypes.INT, description="Number of items per page"),
    ],
    responses={200: OpenApiTypes.OBJECT},
)
@require_http_methods(["GET"])
@api_view(["GET"])

def book_list(request):
    try:
        books = Book.objects.filter(is_active=True)

        # Apply filters
        category = request.GET.get("categoryId")
        if category:
            books = books.filter(category__id=category)

        title = request.GET.get("title")
        if title:
            books = books.filter(title__icontains=title)

        author = request.GET.get("author")
        if author:
            books = books.filter(authors__first_name__icontains=author) | books.filter(authors__last_name__icontains=author)

        publisher = request.GET.get("publisher")
        if publisher:
            books = books.filter(publisher__name__icontains=publisher)

        status = request.GET.get("status")
        if status:
            books = books.filter(status=status)

        min_price = request.GET.get("min_price")
        if min_price:
            books = books.filter(price__gte=min_price)

        max_price = request.GET.get("max_price")
        if max_price:
            books = books.filter(price__lte=max_price)

        start_date = request.GET.get("start_date")
        if start_date:
            books = books.filter(published_date__gte=start_date)

        end_date = request.GET.get("end_date")
        if end_date:
            books = books.filter(published_date__lte=end_date)

        # Pagination
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 10)
        paginator = Paginator(books, page_size)
        paginated_books = paginator.get_page(page)

        # Prepare response data
        books_data = [
            {
                "id": book.id,
                "title": book.title,
                "description": book.description,
                "isbn": book.isbn,
                "price": float(book.price),
                "published_date": book.published_date,
                "stock_quantity": book.stock_quantity,
                "status": book.status,
                "authors": [f"{author.first_name} {author.last_name}" for author in book.authors.all()],
                "publisher": book.publisher.name if book.publisher else None,
                "discount_percent": book.discount_percent,
            }
            for book in paginated_books
        ]
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({
        "total": paginator.count,
        "page": paginated_books.number,
        "page_size": page_size,
        "results": books_data,
    }, safe=False)

# ============ Book Detail ============
@extend_schema(
    summary="Get Book by ISBN",
    description="Retrieve details of a book by its ISBN number.",
    parameters=[
        OpenApiParameter("isbn",type=OpenApiTypes.STR, location=OpenApiParameter.PATH, description="ISBN number of the book to retrieve"),
    ],
)
@api_view(["GET"])
@require_http_methods(["GET"])
def get_book_by_isbn(request, isbn):
    try:
        book = Book.objects.get(Q(isbn=isbn) & Q(is_active=True))
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    except Book.MultipleObjectsReturned:
        return JsonResponse({'error': 'Multiple books found with the same ISBN'}, status=500)
    return JsonResponse({
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "isbn": book.isbn,
        "price": float(book.price),
        "published_date": book.published_date,
        "stock_quantity": book.stock_quantity,
        "status": book.status,
        "authors": [f"{author.first_name} {author.last_name}" for author in book.authors.all()],
        "publisher": book.publisher.name if book.publisher else None,
        "discount_percent": book.discount_percent,
    })
@api_view(["GET"])
def get_book_categories(request):
    categories = Category.objects.filter(is_active=True)
    data = [{ "name": category.name, "description": category.description} for category in categories]
    return JsonResponse(data, safe=False)
