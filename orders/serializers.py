from rest_framework import serializers
from products.serializers import ProductListSerializer
from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'total_price']
        read_only_fields = ['id', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_items']
        read_only_fields = ['id', 'user', 'total_price', 'total_items']


class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'payment_status', 'shipping_address', 
            'shipping_city', 'shipping_state', 'shipping_country', 
            'shipping_postal_code', 'shipping_phone', 'payment_method', 
            'payment_details', 'total_price', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_price', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'shipping_city', 'shipping_state', 
            'shipping_country', 'shipping_postal_code', 'shipping_phone', 
            'payment_method'
        ]
    
    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.get(user=user)
        
        if not cart.items.exists():
            raise serializers.ValidationError({"cart": "Cart is empty"})
        
        # Create order
        order = Order.objects.create(
            user=user,
            total_price=cart.total_price,
            **validated_data
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear cart
        cart.items.all().delete()
        
        return order


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_id', 'amount', 'status', 'payment_method', 'payment_details', 'created_at']
        read_only_fields = ['id', 'created_at']