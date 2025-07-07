from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet, PaymentViewSet, WishlistViewSet

app_name = 'orders'

router = DefaultRouter()
router.register('carts', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')
router.register('payments', PaymentViewSet, basename='payment')
router.register('wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]
