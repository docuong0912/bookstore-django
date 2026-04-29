from django.contrib import admin

from Book.models import Author, Book, Category, Publisher

# Register your models here.
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Category)
