from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_details', 'quantity', 'total_price']
        read_only_fields = ['cart']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['user']


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'quantity', 'price', 'total_price']
        read_only_fields = ['order', 'price']


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'payment_status', 'total_price', 'created_at']
        read_only_fields = ['user']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'payment_status', 'shipping_address', 'shipping_city',
            'shipping_state', 'shipping_country', 'shipping_postal_code', 'shipping_phone',
            'payment_method', 'payment_details', 'total_price', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_price']


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'shipping_city', 'shipping_state', 'shipping_country',
            'shipping_postal_code', 'shipping_phone', 'payment_method'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_id', 'amount', 'status', 'payment_method', 'payment_details', 'created_at']
        read_only_fields = ['order']