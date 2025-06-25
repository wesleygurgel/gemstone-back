from rest_framework import serializers
from .models import Category, Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_main']


class ProductListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'available', 'category', 'category_name', 'featured', 'main_image']
    
    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if not main_image:
            main_image = obj.images.first()
        
        if main_image:
            return {
                'id': main_image.id,
                'image': main_image.image.url if main_image.image else None,
                'alt_text': main_image.alt_text
            }
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'stock', 'available', 
                  'category', 'category_name', 'featured', 'images', 'created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'available', 'category', 'featured']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image']


class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'products']