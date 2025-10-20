from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer
from home.utils import send_email 

class OrderDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a single order by its ID.
    Only the customer who placed the order can access it.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Restrict users to only their own orders
        return Order.objects.filter(customer=self.request.user)
