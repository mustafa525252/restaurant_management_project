from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError, IntegrityError
from django.core.mail import BadHeaderError, SMTPException
import logging
from rest_framework.exceptions import NotFound
from .models import (
    MenuCategory, 
    Table, 
    Order,
    ContactFormSubmission,
    Restaurant,
    MenuItem,
    DailySpecial,
    UserReview,
    Review,
    MenuItem
)

from .serializers import (
    MenuCategorySerializer,
    TableSerializer,
    OrderSerializer,
    ContactFormSubmissionSerializer,
    IngredientSerializer,
    RestaurantSerializer,
    MenuItemSerializer,
    DailySpecialSerializer,
    UserReviewSerializer,
    ReviewSerializer,
    MenuItemAvailabilitySerializer,
    MenuItemSearchSerializer
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

class MenuItemIngredientsView(generics.RetrieveAPIView):
    """
    API endpoint to get all ingredients for a specific MenuItem.
    """
    queryset = MenuItem.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        try:
            menu_item = MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            raise NotFound("Menu item not found.")

        ingredients = menu_item.ingredients.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)

class FeaturedMenuItemsView(generics.ListAPIView):
    """
    API endpoint to list all featured menu items.
    """
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        return MenuItem.objects.filter(is_featured=True)
    
class MenuCategoryListCreateView(generics.ListCreateAPIView):
    """
    GET → List all categories
    POST → Create a new category
    """
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer


class MenuCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET → Retrieve a category
    PUT/PATCH → Update a category
    DELETE → Delete a category
    """
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    
class DailySpecialListView(APIView):
    """
    Retrieve all available daily specials.
    """
    def get(self, request):
        specials = DailySpecial.objects.filter(is_available=True)
        serializer = DailySpecialSerializer(specials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RestaurantListAPIView(generics.ListAPIView):
    """
    API endpoint to return all restaurant information.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    
# 1️⃣ Create a new review
class UserReviewCreateAPIView(generics.CreateAPIView):
    queryset = UserReview.objects.all()
    serializer_class = UserReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 2️⃣ Retrieve all reviews for a specific menu item
class MenuItemReviewsListAPIView(generics.ListAPIView):
    serializer_class = UserReviewSerializer

    def get_queryset(self):
        menu_item_id = self.kwargs.get('menu_item_id')
        if not menu_item_id:
            raise NotFound("Menu item ID not provided.")
        return UserReview.objects.filter(menu_item_id=menu_item_id)
    
class CreateReviewAPIView(APIView):
    """
    API endpoint for creating new user reviews.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"message": "Review submitted successfully!", "review": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
        
class UpdateMenuItemAvailabilityAPIView(APIView):
    """
    API endpoint to update the availability of a specific menu item.
    """

    def patch(self, request, pk):
        try:
            menu_item = MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            return Response(
                {"error": "Menu item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MenuItemAvailabilitySerializer(menu_item, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": f"Availability for '{menu_item.name}' updated successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class MenuItemSearchView(APIView):
    """
    API endpoint for searching menu items by name (case-insensitive).
    Example: /api/menu/search/?q=pizza
    """

    def get(self, request):
        query = request.GET.get('q', '').strip()

        if not query:
            return Response(
                {"error": "Please provide a search term using the 'q' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Case-insensitive search using __icontains
        items = MenuItem.objects.filter(name__icontains=query)

        serializer = MenuItemSearchSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)