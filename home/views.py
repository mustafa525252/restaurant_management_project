from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import DatabaseError, IntegrityError
from django.core.mail import BadHeaderError, SMTPException
import logging

from .models import MenuCategory, Table, Order, ContactFormSubmission
from .serializers import (
    MenuCategorySerializer,
    TableSerializer,
    OrderSerializer,
    ContactFormSubmissionSerializer
)
from .utils import send_order_confirmation_email

# Setup logger
logger = logging.getLogger(__name__)


# -----------------------------
# Menu Categories
# -----------------------------
class MenuCategoryListView(ListAPIView):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer


# -----------------------------
# Tables
# -----------------------------
class TableDetailAPIView(generics.RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    lookup_field = 'pk'


class AvailableTablesAPIView(generics.ListAPIView):
    """
    Returns a list of tables that are currently available for reservation.
    """
    serializer_class = TableSerializer

    def get_queryset(self):
        return Table.objects.filter(is_available=True)


# -----------------------------
# Orders
# -----------------------------
class CreateOrderAPIView(APIView):
    """
    Handles order creation and sends a confirmation email upon success.
    """
    def post(self, request):
        serializer = OrderSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Save the order safely
            order = serializer.save()
        except IntegrityError as e:
            logger.error(f"IntegrityError while saving order: {e}")
            return Response(
                {"error": "Invalid data. Could not save order."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as e:
            logger.error(f"Database error during order creation: {e}")
            return Response(
                {"error": "A database error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.exception("Unexpected error while saving order")
            return Response(
                {"error": f"Unexpected error while creating order: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Extract order details
        order_id = order.id
        customer_email = getattr(order.customer, "email", None)
        customer_name = getattr(order.customer, "name", "Customer")
        order_items = [item.name for item in getattr(order, "items", []).all()]
        total_amount = getattr(order, "total_amount", 0)

        if not customer_email:
            return Response(
                {"error": "Customer email not found. Cannot send confirmation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Attempt to send email
        try:
            success = send_order_confirmation_email(
                order_id=order_id,
                customer_email=customer_email,
                customer_name=customer_name,
                order_items=order_items,
                total_amount=total_amount
            )
        except (SMTPException, BadHeaderError) as e:
            logger.warning(f"Email sending failed for order {order_id}: {e}")
            return Response(
                {"warning": f"Order created, but email failed to send due to: {str(e)}"},
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            logger.exception("Unexpected error while sending email")
            return Response(
                {"warning": f"Order created, but email failed unexpectedly: {str(e)}"},
                status=status.HTTP_202_ACCEPTED
            )

        # Success response
        if success:
            return Response(
                {"message": "Order created successfully. Confirmation email sent."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"warning": "Order created, but confirmation email could not be sent."},
                status=status.HTTP_202_ACCEPTED
            )


# -----------------------------
# Contact Form Submission
# -----------------------------
class ContactFormSubmissionView(generics.CreateAPIView):
    queryset = ContactFormSubmission.objects.all()
    serializer_class = ContactFormSubmissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Thank you for contacting us! We’ve received your message."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
