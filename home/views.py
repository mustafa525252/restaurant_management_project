from django.shortcuts import render
from rest_framework import generics
from rest_framework.generics import ListAPIView
from .models import MenuCategory,Table,Order
from .serializers import MenuCategorySerializer, TableSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import OrderSerializer
from .utils import send_order_confirmation_email

# Create your views here.

class MenuCategoryListView(ListAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer

class TableDetailAPIView(generics.RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    lookup_field = 'pk'
    
class AvailableTablesAPIView(generics.ListAPIView):
    queryset = Table.objects.filter(is_available=True)
    serializer_class = TableSerializer

class AvailableTablesAPIView(generics.ListAPIView):
    queryset = Table.objects.filter(is_available=True)
    serializer_class = TableSerializer
    
class CreateOrderAPIView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()  # Saves the order to DB

            # Prepare order details for email
            order_id = order.id
            customer_email = order.customer.email
            customer_name = order.customer.name
            order_items = [item.name for item in order.items.all()]
            total_amount = order.total_amount

            # Call the reusable email function
            success = send_order_confirmation_email(
                order_id=order_id,
                customer_email=customer_email,
                customer_name=customer_name,
                order_items=order_items,
                total_amount=total_amount
            )

            if success:
                return Response({"message": "Order created and email sent successfully."})
            else:
                return Response({"message": "Order created, but email failed to send."})
        
        return Response(serializer.errors, status=400)