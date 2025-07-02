import sys
import json
import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from core.utils import console_menu, wait_prompt
from accounts.models import UserProfile
from products.models import Category, Product
from orders.models import Cart, CartItem, Order, OrderItem, Payment
from lib.ia.deepseek_service import DeepSeekService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Database management and population for Gemstone application'

    def add_arguments(self, parser):
        parser.add_argument('--debug', action="store_true")
        parser.add_argument('--quiet', action="store_true")

    def debug(self, message):
        if not self._quiet:
            self.stdout.write(message)

    def handle(self, *args, **options):
        self._quiet = options["quiet"]
        try:
            self._handle(**options)
        except Exception as error:
            logger.exception('Erro inesperado em console_database: %s', error)
            raise

    def _handle(self, **options):
        self.debug("== console_database")
        start_time = datetime.now()
        self.debug(f"= Started at: {start_time}")

        actions = [
            [1, 'Populate database with sample data', self.populate_database, options],
            [2, 'Generate product categories using AI', self.generate_ai_categories, options],
            [3, 'Generate products for categories using AI', self.generate_ai_products, options],
        ]

        console_menu(actions)

        end_time = datetime.now()
        self.debug(f"= Finished at: {end_time}")
        self.debug(f"= Total elapsed time: {end_time - start_time}")

    def populate_database(self, options):
        """
        Populate the database with sample data related to precious metals trading
        """
        self.debug("== Populate database with sample data")

        # Confirm with the user before proceeding
        if not wait_prompt("This will populate the database with sample data. Are you sure you want to proceed?"):
            self.debug("Operation cancelled by user.")
            return

        self.debug("Starting database population...")

        # Wrap all database operations in a transaction for atomicity
        with transaction.atomic():
            # Create sample users
            self.debug("Creating sample users...")
            self._create_sample_users()

            # Create product categories
            self.debug("Creating product categories...")
            self._create_product_categories()

            # Create products
            self.debug("Creating sample products...")
            self._create_sample_products()

            # Create sample orders
            self.debug("Creating sample orders...")
            self._create_sample_orders()

        self.debug("Database population completed successfully!")

    def _create_sample_users(self):
        """Create sample users for the application"""
        users_data = [
            {
                'username': 'john_trader',
                'email': 'john@example.com',
                'password': 'securepass123',
                'first_name': 'John',
                'last_name': 'Smith',
                'profile': {
                    'phone_number': '+1 555-123-4567',
                    'address': '123 Gold Street',
                    'city': 'New York',
                    'state': 'NY',
                    'country': 'USA',
                    'postal_code': '10001'
                }
            },
            {
                'username': 'dubai_gold',
                'email': 'ahmed@example.com',
                'password': 'dubai2023',
                'first_name': 'Ahmed',
                'last_name': 'Al-Mansour',
                'profile': {
                    'phone_number': '+971 50 123 4567',
                    'address': 'Gold Souk, Shop 45',
                    'city': 'Dubai',
                    'state': 'Dubai',
                    'country': 'UAE',
                    'postal_code': '12345'
                }
            },
            {
                'username': 'swiss_metals',
                'email': 'hans@example.com',
                'password': 'swiss2023',
                'first_name': 'Hans',
                'last_name': 'Mueller',
                'profile': {
                    'phone_number': '+41 44 123 4567',
                    'address': 'Bahnhofstrasse 123',
                    'city': 'Zurich',
                    'state': 'Zurich',
                    'country': 'Switzerland',
                    'postal_code': '8001'
                }
            }
        ]

        for user_data in users_data:
            profile_data = user_data.pop('profile')

            # Check if user already exists
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(**user_data)
                self.debug(f"Created user: {user.username}")
            else:
                user = User.objects.get(username=user_data['username'])

            # Create user profile
            if not UserProfile.objects.filter(user__username=user_data['username']).exists():
                UserProfile.objects.create(user=user, **profile_data)
                self.debug(f"Created profile for: {user.username}")
            else:
                self.debug(f"User {user_data['username']} already exists, skipping.")

    def _create_product_categories(self):
        """Create product categories for precious metals"""
        categories = [
            {
                'name': 'Gold Bullion',
                'description': 'Investment grade gold bullion in various forms and weights.'
            },
            {
                'name': 'Silver Products',
                'description': 'Silver bullion, coins, and investment products.'
            },
            {
                'name': 'Platinum & Palladium',
                'description': 'Platinum and palladium investment products.'
            },
            {
                'name': 'Numismatic Coins',
                'description': 'Collectible gold and silver coins with numismatic value.'
            },
            {
                'name': 'Jewelry',
                'description': 'Fine jewelry made from precious metals.'
            }
        ]

        for category_data in categories:
            # Check if category already exists
            if not Category.objects.filter(name=category_data['name']).exists():
                category = Category.objects.create(**category_data)
                self.debug(f"Created category: {category.name}")
            else:
                self.debug(f"Category {category_data['name']} already exists, skipping.")

    def _create_sample_products(self):
        """Create sample products for precious metals trading"""
        products_data = [
            {
                'category_name': 'Gold Bullion',
                'products': [
                    {
                        'name': '1 oz Gold Bar',
                        'description': 'Pure 999.9 fine gold bar, 1 troy ounce. Produced by PAMP Suisse.',
                        'price': Decimal('1950.00'),
                        'stock': 50,
                        'featured': True
                    },
                    {
                        'name': '1 kg Gold Bar',
                        'description': 'Pure 999.9 fine gold bar, 1 kilogram. Produced by Emirates Gold.',
                        'price': Decimal('62500.00'),
                        'stock': 10,
                        'featured': True
                    },
                    {
                        'name': 'American Gold Eagle 1 oz',
                        'description': 'Official gold bullion coin of the United States, 1 troy ounce of 91.67% pure gold.',
                        'price': Decimal('2050.00'),
                        'stock': 100,
                        'featured': False
                    }
                ]
            },
            {
                'category_name': 'Silver Products',
                'products': [
                    {
                        'name': '100 oz Silver Bar',
                        'description': 'Pure 999 fine silver bar, 100 troy ounces.',
                        'price': Decimal('2700.00'),
                        'stock': 30,
                        'featured': False
                    },
                    {
                        'name': 'Silver Canadian Maple Leaf 1 oz',
                        'description': 'Official silver bullion coin of Canada, 1 troy ounce of 999.9 fine silver.',
                        'price': Decimal('28.50'),
                        'stock': 500,
                        'featured': True
                    }
                ]
            },
            {
                'category_name': 'Platinum & Palladium',
                'products': [
                    {
                        'name': '1 oz Platinum Bar',
                        'description': 'Pure 999.5 fine platinum bar, 1 troy ounce.',
                        'price': Decimal('950.00'),
                        'stock': 25,
                        'featured': False
                    },
                    {
                        'name': '1 oz Palladium Maple Leaf',
                        'description': 'Canadian Palladium Maple Leaf, 1 troy ounce of 999.5 fine palladium.',
                        'price': Decimal('1050.00'),
                        'stock': 15,
                        'featured': False
                    }
                ]
            },
            {
                'category_name': 'Numismatic Coins',
                'products': [
                    {
                        'name': 'Gold Sovereign - King George V',
                        'description': 'Historic British gold sovereign coin from the reign of King George V, 7.32g of 22 carat gold.',
                        'price': Decimal('550.00'),
                        'stock': 20,
                        'featured': True
                    }
                ]
            },
            {
                'category_name': 'Jewelry',
                'products': [
                    {
                        'name': '24K Gold Chain - 50g',
                        'description': 'Pure 24 karat gold chain, 50 grams, handcrafted in Dubai.',
                        'price': Decimal('3200.00'),
                        'stock': 5,
                        'featured': True
                    }
                ]
            }
        ]

        for category_data in products_data:
            try:
                category = Category.objects.get(name=category_data['category_name'])

                for product_data in category_data['products']:
                    # Check if product already exists
                    if not Product.objects.filter(name=product_data['name']).exists():
                        product = Product.objects.create(
                            category=category,
                            **product_data
                        )
                        self.debug(f"Created product: {product.name}")
                    else:
                        self.debug(f"Product {product_data['name']} already exists, skipping.")
            except Category.DoesNotExist:
                self.debug(f"Category {category_data['category_name']} does not exist, skipping products.")

    def _create_sample_orders(self):
        """Create sample orders for the application"""
        # Get users
        users = User.objects.all()
        if not users:
            self.debug("No users found, skipping order creation.")
            return

        # Get products
        products = Product.objects.all()
        if not products:
            self.debug("No products found, skipping order creation.")
            return

        # Create orders for each user
        for user in users:
            try:
                # Try to access the user's profile to check if it exists
                profile = user.profile

                # Create cart if it doesn't exist
                cart, created = Cart.objects.get_or_create(user=user)
                if created:
                    self.debug(f"Created cart for user: {user.username}")

                # Add random products to cart
                for _ in range(random.randint(1, 3)):
                    product = random.choice(products)
                    quantity = random.randint(1, 3)

                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=product,
                        defaults={'quantity': quantity}
                    )

                    if not created:
                        cart_item.quantity = quantity
                        cart_item.save()

                    self.debug(f"Added {quantity} x {product.name} to cart for {user.username}")

                # Create 1-3 orders for each user
                for _ in range(random.randint(1, 3)):
                    # Calculate total price from cart items
                    total_price = sum(item.product.price * item.quantity for item in cart.items.all())

                    # Create order
                    order = Order.objects.create(
                        user=user,
                        status=random.choice(['pending', 'processing', 'shipped', 'delivered']),
                        payment_status=random.choice(['pending', 'paid']),
                        shipping_address=profile.address or '123 Default St',
                        shipping_city=profile.city or 'Default City',
                        shipping_state=profile.state or 'Default State',
                        shipping_country=profile.country or 'Default Country',
                        shipping_postal_code=profile.postal_code or '12345',
                        shipping_phone=profile.phone_number or '+1 555-555-5555',
                        payment_method=random.choice(['credit_card', 'bank_transfer', 'paypal']),
                        payment_details={'transaction_id': f'txn_{random.randint(10000, 99999)}'},
                        total_price=total_price
                    )
                    self.debug(f"Created order for {user.username}: Order #{order.id}")

                    # Add order items
                    for cart_item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.price
                        )
                        self.debug(f"Added {cart_item.quantity} x {cart_item.product.name} to order #{order.id}")

                    # Create payment if order is paid
                    if order.payment_status == 'paid':
                        Payment.objects.create(
                            order=order,
                            payment_id=f'pmt_{random.randint(10000, 99999)}',
                            amount=order.total_price,
                            status='completed',
                            payment_method=order.payment_method,
                            payment_details={'transaction_date': (
                                    datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()}
                        )
                        self.debug(f"Created payment for order #{order.id}")
            except User.profile.RelatedObjectDoesNotExist:
                self.debug(f"Skipping order creation for user {user.username} - no profile found.")

    def generate_ai_categories(self, options):
        """
        Generate product categories using AI and add them to the database
        """
        self.debug("== Generate product categories using AI")

        # Confirm with the user before proceeding
        if not wait_prompt("This will generate new product categories using AI. Are you sure you want to proceed?"):
            self.debug("Operation cancelled by user.")
            return

        self.debug("Sending prompt to AI service...")

        # The prompt as specified in the requirements
        prompt = """Considere o seguinte contexto:

Segmento: Comércio internacional de metais preciosos (especialmente ouro).  
Atuação: Operações logísticas, compras e importação de ouro com atuação global (com foco em Dubai).

Com base nisso, retorne 4 categorias de produtos que sejam relevantes para esse tipo de negócio. O retorno deve ser em formato JSON, com a seguinte estrutura:

{
  "categorias": ["categoria_1", "categoria_2", "categoria_3", "categoria_4"]
}

Não inclua explicações ou qualquer texto fora do JSON."""

        # Create an instance of DeepSeekService
        deepseek_service = DeepSeekService()

        # Define a system message to provide context
        system_message = "You are an AI assistant specialized in international precious metals trading. Your task is to generate relevant product categories for a business in this industry."

        # Call the AI service with the system message
        response = deepseek_service.send_prompt(
            prompt=prompt,
            system_message=system_message
        )

        # Check if there was an error
        if isinstance(response, dict) and 'error' in response:
            self.debug(f"Error from AI service: {response['error']}")
            return

        try:
            # Extract the content from the response
            ai_content = response.choices[0].message.content

            # Parse the JSON response
            self.debug("Parsing AI response...")

            # Try to extract JSON from the response if it contains other text
            try:
                # Find JSON in the response if there's any text around it
                start_idx = ai_content.find('{')
                end_idx = ai_content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = ai_content[start_idx:end_idx]
                    categories_data = json.loads(json_str)
                else:
                    categories_data = json.loads(ai_content)
            except json.JSONDecodeError:
                self.debug(f"Failed to parse JSON from AI response: {ai_content}")
                return

            # Extract categories from the parsed JSON
            categories = categories_data.get('categorias', [])

            if not categories:
                self.debug("No categories found in AI response.")
                return

            self.debug(f"AI generated {len(categories)} categories: {', '.join(categories)}")

            # Confirm with the user before adding to database
            if not wait_prompt("Do you want to add these categories to the database?"):
                self.debug("Operation cancelled by user.")
                return

            # Add categories to the database
            with transaction.atomic():
                for category_name in categories:
                    # Check if category already exists
                    if not Category.objects.filter(name=category_name).exists():
                        category = Category.objects.create(
                            name=category_name,
                            description=f"AI-generated category for {category_name} in precious metals trading."
                        )
                        self.debug(f"Created category: {category.name}")
                    else:
                        self.debug(f"Category {category_name} already exists, skipping.")

            self.debug("AI category generation completed successfully!")

        except Exception as e:
            self.debug(f"Error processing AI response: {str(e)}")
            logger.exception("Error in generate_ai_categories")

    def generate_ai_products(self, options):
        """
        Generate products for existing categories using AI and add them to the database
        """
        self.debug("== Generate products for categories using AI")

        # Get all categories from the database
        categories = Category.objects.all()

        if not categories.exists():
            self.debug("No categories found in the database. Please create categories first.")
            return

        # Confirm with the user before proceeding
        if not wait_prompt("This will generate new products for each category using AI. Are you sure you want to proceed?"):
            self.debug("Operation cancelled by user.")
            return

        self.debug(f"Found {categories.count()} categories in the database.")

        # Create an instance of DeepSeekService
        deepseek_service = DeepSeekService()

        # Define a system message to provide context
        system_message = "You are an AI assistant specialized in international precious metals trading. Your task is to generate realistic products for each category in this industry."

        # Process each category
        for category in categories:
            self.debug(f"Processing category: {category.name} (slug: {category.slug})")

            # Construct the prompt for this category
            prompt = f"""Considere o seguinte contexto:

Segmento: Comércio internacional de metais preciosos (especialmente ouro).
Atuação: Operações logísticas, compras e importação de ouro com atuação global (com foco em Dubai).
Categoria de produto: {category.name}
Descrição da categoria: {category.description or 'N/A'}

Com base nisso, crie 4 produtos para esta categoria. O retorno deve ser em formato JSON, com a seguinte estrutura:

{{
  "{category.slug}": [
    {{
      "name": "Nome do Produto 1",
      "description": "Descrição detalhada do produto 1",
      "price": 1000.00,
      "price_discount": 900.00,
      "stock": 50,
      "available": true,
      "featured": true
    }},
    {{
      "name": "Nome do Produto 2",
      "description": "Descrição detalhada do produto 2",
      "price": 2000.00,
      "price_discount": null,
      "stock": 30,
      "available": true,
      "featured": false
    }},
    ...
  ]
}}

Não inclua explicações ou qualquer texto fora do JSON. Os preços devem ser realistas para o tipo de produto."""

            self.debug(f"Sending prompt to AI service for category: {category.name}...")

            # Call the AI service with the system message
            response = deepseek_service.send_prompt(
                prompt=prompt,
                system_message=system_message,
                max_tokens=2000  # Increase token limit for larger responses
            )

            # Check if there was an error
            if isinstance(response, dict) and 'error' in response:
                self.debug(f"Error from AI service for category {category.name}: {response['error']}")
                continue  # Skip to the next category

            try:
                # Extract the content from the response
                ai_content = response.choices[0].message.content

                # Parse the JSON response
                self.debug(f"Parsing AI response for category: {category.name}...")

                # Try to extract JSON from the response if it contains other text
                try:
                    # Find JSON in the response if there's any text around it
                    start_idx = ai_content.find('{')
                    end_idx = ai_content.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = ai_content[start_idx:end_idx]
                        products_data = json.loads(json_str)
                    else:
                        products_data = json.loads(ai_content)
                except json.JSONDecodeError:
                    self.debug(f"Failed to parse JSON from AI response for category {category.name}: {ai_content}")
                    continue  # Skip to the next category

                # Extract products from the parsed JSON
                products = products_data.get(category.slug, [])

                if not products:
                    self.debug(f"No products found in AI response for category {category.name}.")
                    continue  # Skip to the next category

                self.debug(f"AI generated {len(products)} products for category {category.name}")

                # Display the generated products
                for i, product in enumerate(products, 1):
                    self.debug(f"  Product {i}: {product.get('name', 'Unnamed product')}")

                # Confirm with the user before adding to database
                if not wait_prompt(f"Do you want to add these products to the category '{category.name}'?"):
                    self.debug(f"Skipping product creation for category {category.name}.")
                    continue  # Skip to the next category

                # Add products to the database
                with transaction.atomic():
                    for product_data in products:
                        # Check if product already exists
                        product_name = product_data.get('name')
                        if not product_name:
                            self.debug("Product name is missing, skipping.")
                            continue

                        if Product.objects.filter(name=product_name).exists():
                            self.debug(f"Product {product_name} already exists, skipping.")
                            continue

                        # Convert price and price_discount to Decimal
                        try:
                            price = Decimal(str(product_data.get('price', 0)))

                            # Handle price_discount which might be null
                            price_discount_raw = product_data.get('price_discount')
                            price_discount = Decimal(str(price_discount_raw)) if price_discount_raw is not None else None

                            # Create the product
                            product = Product.objects.create(
                                name=product_name,
                                description=product_data.get('description', ''),
                                price=price,
                                price_discount=price_discount,
                                stock=int(product_data.get('stock', 0)),
                                available=bool(product_data.get('available', True)),
                                featured=bool(product_data.get('featured', False)),
                                category=category
                            )
                            self.debug(f"Created product: {product.name} (slug: {product.slug})")
                        except (ValueError, TypeError) as e:
                            self.debug(f"Error creating product {product_name}: {str(e)}")
                            continue

                self.debug(f"Product generation for category {category.name} completed successfully!")

            except Exception as e:
                self.debug(f"Error processing AI response for category {category.name}: {str(e)}")
                logger.exception(f"Error in generate_ai_products for category {category.name}")

        self.debug("AI product generation process completed!")
