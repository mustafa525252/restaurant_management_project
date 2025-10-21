from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from home.models import MenuItem
from orders.models import Order, OrderItem, OrderStatus


class OrderTotalTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='john', password='12345')
        self.status = OrderStatus.objects.create(name='pending')
        self.order = Order.objects.create(
            customer=self.user,
            order_status=self.status,
            name='Test Order',
            quantity=1,
            price=Decimal('0.00')
        )

        self.item1 = MenuItem.objects.create(name='Pizza', price=Decimal('10.00'))
        self.item2 = MenuItem.objects.create(name='Burger', price=Decimal('5.50'))

        OrderItem.objects.create(order=self.order, menu_item=self.item1, quantity=2, price=self.item1.price)
        OrderItem.objects.create(order=self.order, menu_item=self.item2, quantity=3, price=self.item2.price)

    def test_calculate_total(self):
        total = self.order.calculate_total()
        expected_total = (Decimal('10.00') * 2) + (Decimal('5.50') * 3)
        self.assertEqual(total, expected_total)
