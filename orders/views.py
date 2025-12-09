from rest_framework import generics, permissions
from .models import (
    Order,
    OrderStatus,
    PaymentMethod,
    Review,
    Table
)
from .serializers import (
    OrderSerializer,
    OrderStatusSerializer,
    OrderStatusUpdateSerializer,
    PaymentMethodSerializer,
    ReviewSerializer,
    OrderSummarySerializer,
    TableSerializer
)
from django.db import DatabaseError
from rest_framework.pagination import PageNumberPagination
from home.utils import send_email 
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view

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
            
class UpdateOrderStatusView(APIView):
    """
    PUT /api/orders/<order_id>/update-status/
    Body: {"status": "processing"}
    """

    def put(self, request, order_id):
        # 1️⃣ Check if order exists
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2️⃣ Validate the new status
        new_status_name = request.data.get("status")
        if not new_status_name:
            return Response(
                {"error": "Status field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            status_obj = OrderStatus.objects.get(name__iexact=new_status_name)
        except OrderStatus.DoesNotExist:
            return Response(
                {"error": f"Invalid status '{new_status_name}'. Allowed statuses: {[s.name for s in OrderStatus.objects.all()]}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3️⃣ Update the order
        order.order_status = status_obj
        order.save()

        return Response(
            {"message": f"Order {order.order_id} status updated to '{status_obj.name}'."},
            status=status.HTTP_200_OK
        )
        

@api_view(['GET'])
def get_order_status(request, order_id):
    """
    Retrieve the current status of an order given its order ID.
    Returns a JSON response with the order ID and status.
    """
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            "order_id": order.order_id,
            "status": order.order_status.name if order.order_status else "No Status"
        },
        status=status.HTTP_200_OK
    )
    
class OrderStatusRetrieveView(generics.RetrieveAPIView):
    serializer_class = OrderStatusSerializer
    lookup_field = 'order_id'

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            serializer = self.serializer_class(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        
class PaymentMethodListAPIView(generics.ListAPIView):
    queryset = PaymentMethod.objects.filter(is_active=True)  # ✅ Only active methods
    serializer_class = PaymentMethodSerializer
    
class ReviewListView(generics.ListAPIView):
    """
    API endpoint to retrieve all restaurant reviews.
    Includes pagination and error handling.
    """
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except DatabaseError:
            return Response(
                {"error": "Unable to retrieve reviews at this time."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class OrderHistoryPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class UserOrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = OrderHistoryPagination

    def get_queryset(self):
        """
        Return all orders belonging to the authenticated user.
        """
        return Order.objects.filter(customer=self.request.user).order_by('-order_date')
    
class OrderSummaryView(generics.RetrieveAPIView):
    serializer_class = OrderSummarySerializer
    lookup_field = 'order_id'
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
class TableListView(generics.ListAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer