from django.urls import path
from . import views

urlpatterns = [
    # API schema and documentation
    
    # CRUD endpoints for books
    path('', views.book_list, name='book_list'),
    path('isbn/<str:isbn>/', views.get_book_by_isbn, name='book_detail'),
    path('categories/', views.get_book_categories, name='book_categories'),
]