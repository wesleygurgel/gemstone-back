import sys
import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.db import transaction
from core.utils import console_menu, wait_prompt
from accounts.models import UserProfile
from products.models import Category, Product
from orders.models import Cart, CartItem, Order, OrderItem, Payment

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
