from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Cart, CartItem, Order, OrderItem, Payment, Wishlist, WishlistItem
from .serializers import (
    CartSerializer, CartItemSerializer,
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderItemSerializer, PaymentSerializer,
    WishlistSerializer, WishlistItemSerializer
)


@extend_schema_view(
    list=extend_schema(description="List all carts"),
    retrieve=extend_schema(description="Retrieve a cart by ID"),
)
class CartViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to the cart"""
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']

            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            # If item exists, update quantity
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """Remove an item from the cart"""
        cart = self.get_object()
        try:
            item_id = request.data.get('item_id')
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        """Update an item in the cart"""
        cart = self.get_object()
        try:
            item_id = request.data.get('item_id')
            quantity = request.data.get('quantity')

            item = CartItem.objects.get(id=item_id, cart=cart)
            item.quantity = quantity
            item.save()

            return Response(CartItemSerializer(item).data)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear all items from the cart"""
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(description="List all orders"),
    retrieve=extend_schema(description="Retrieve an order by ID"),
    create=extend_schema(description="Create a new order"),
)
class OrderViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status']
    ordering_fields = ['created_at', 'total_price']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderListSerializer

    def perform_create(self, serializer):
        user = self.request.user

        # Get user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if cart has items
        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price
        total_price = cart.total_price

        # Create order
        order = serializer.save(
            user=user,
            total_price=total_price
        )

        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

            # Increment sales_count for the product
            product = cart_item.product
            product.sales_count += cart_item.quantity
            product.save()

        # Clear cart
        cart.items.all().delete()

        return order


@extend_schema_view(
    list=extend_schema(description="List all payments"),
    retrieve=extend_schema(description="Retrieve a payment by ID"),
    create=extend_schema(description="Create a new payment"),
)
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=user)

    def perform_create(self, serializer):
        order_id = self.request.data.get('order')
        try:
            order = Order.objects.get(id=order_id, user=self.request.user)
            serializer.save(order=order)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(description="Get the current user's wishlist"),
    add_item=extend_schema(description="Add a product to the wishlist"),
    remove_item=extend_schema(description="Remove a product from the wishlist"),
)
class WishlistViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def get_object(self):
        # Get or create wishlist for the current user
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist

    def list(self, request):
        """Get the current user's wishlist"""
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add a product to the wishlist"""
        wishlist = self.get_object()
        serializer = WishlistItemSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.validated_data['product']

            # Check if the item already exists in the wishlist
            if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
                return Response(
                    {"detail": "Product already in wishlist"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the wishlist item
            wishlist_item = WishlistItem.objects.create(
                wishlist=wishlist,
                product=product
            )

            return Response(
                WishlistItemSerializer(wishlist_item).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove a product from the wishlist"""
        wishlist = self.get_object()
        product_id = request.data.get('product_id')

        if not product_id:
            return Response(
                {"detail": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            wishlist_item = WishlistItem.objects.get(
                wishlist=wishlist,
                product_id=product_id
            )
            wishlist_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WishlistItem.DoesNotExist:
            return Response(
                {"detail": "Product not found in wishlist"},
                status=status.HTTP_404_NOT_FOUND
            )
