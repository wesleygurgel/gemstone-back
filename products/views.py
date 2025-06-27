from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer, CategoryDetailSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductImageSerializer
)


@extend_schema_view(
    list=extend_schema(description="List all categories"),
    retrieve=extend_schema(description="Retrieve a category by ID"),
    create=extend_schema(description="Create a new category"),
    update=extend_schema(description="Update a category"),
    partial_update=extend_schema(description="Partially update a category"),
    destroy=extend_schema(description="Delete a category")
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    lookup_field = 'pk'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


@extend_schema_view(
    list=extend_schema(description="List all products"),
    retrieve=extend_schema(description="Retrieve a product by ID"),
    create=extend_schema(description="Create a new product"),
    update=extend_schema(description="Update a product"),
    partial_update=extend_schema(description="Partially update a product"),
    destroy=extend_schema(description="Delete a product")
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    lookup_field = 'pk'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'available', 'featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, slug=None):
        """Upload an image to a product"""
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def images(self, request, slug=None):
        """Get all images for a product"""
        product = self.get_object()
        images = ProductImage.objects.filter(product=product)
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="List all product images"),
    retrieve=extend_schema(description="Retrieve a product image by ID"),
    create=extend_schema(description="Create a new product image"),
    update=extend_schema(description="Update a product image"),
    partial_update=extend_schema(description="Partially update a product image"),
    destroy=extend_schema(description="Delete a product image")
)
class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
