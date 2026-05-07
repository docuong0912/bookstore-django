from rest_framework import serializers

from Cart.models import Cart

class OrderSerializer(serializers.Serializer):
    order_name = serializers.CharField(max_length=255)
    address = serializers.CharField(required=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    province_id = serializers.IntegerField()
    ward_id = serializers.IntegerField()
    cart_id = serializers.IntegerField()
    note = serializers.CharField(required=False, allow_blank=True)
    def validate_cart_id(self, value):
        if not Cart.objects.filter(id=value).exists():
            raise serializers.ValidationError("Cart with the given ID does not exist.")
        return value