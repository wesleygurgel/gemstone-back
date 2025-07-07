from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment, Wishlist, WishlistItem
from products.serializers import ProductListSerializer
from products.models import Product


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
            'id', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_country',
            'shipping_postal_code', 'shipping_phone', 'payment_method'
        ]
        read_only_fields = ['id']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_id', 'amount', 'status', 'payment_method', 'payment_details', 'created_at']
        read_only_fields = ['order']


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_id']
        read_only_fields = ['id']


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'items', 'total_items']
        read_only_fields = ['id']
