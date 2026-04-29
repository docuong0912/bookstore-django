from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

class BaseModel(models.Model):
    created_at = models.DateTimeField( default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True
# ============ Author Model ============
class Author(BaseModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ============ Publisher Model ============
class Publisher(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ============ Category Model ============
class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# ============ Book Model ============
class Book(BaseModel):

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    
    isbn = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    
    published_date = models.DateField()
    pages = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    thumbnail = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['status']),
        ]
        db_table = 'Book'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title

    @property
    def get_price(self):
        """Return discount price if available, otherwise return regular price"""
        return self.discount_price if self.discount_price else self.price

    @property
    def is_in_stock(self):
        """Check if book is in stock"""
        return self.stock_quantity > 0 and self.status == 'available'
    @property
    def discount_percent(self):
        if self.discount_price:
            return (self.price - self.discount_price) / self.price * 100
        return 0
