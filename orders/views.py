from rest_framework import generics, permissions
from .models import Order, OrderStatus
from .serializers import OrderSerializer
from home.utils import send_email 
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView

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

class CancelOrderAPIView(APIView):
    """
    API endpoint to cancel an order by ID.
    Only the customer who placed the order can cancel it.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, order_id):
        try:
            # Get order that belongs to the logged-in user
            order = Order.objects.get(order_id=order_id, customer=request.user)

            # Check if it's already cancelled
            if order.order_status and order.order_status.name.lower() == "cancelled":
                return Response(
                    {"message": "This order is already cancelled."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the 'Cancelled' status
            cancelled_status, _ = OrderStatus.objects.get_or_create(name="Cancelled")

            # Update and save
            order.order_status = cancelled_status
            order.save()

            return Response(
                {"message": f"Order {order.order_id} has been cancelled successfully."},
                status=status.HTTP_200_OK
            )

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found or you do not have permission to cancel it."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to cancel order: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )