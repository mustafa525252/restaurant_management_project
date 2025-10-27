from django.urls import path
from .views import (
    MenuCategoryListCreateView,
    MenuCategoryDetailView,
    TableDetailAPIView,
    AvailableTablesAPIView,
    ContactFormSubmissionView,
    MenuItemIngredientsView,
    FeaturedMenuItemsView,
    DailySpecialListView,
    UserReviewCreateAPIView, 
    MenuItemReviewsListAPIView,
    MenuCategoryListView
)

urlpatterns = [
    # ✅ Menu Category API
    path('api/menu-categories/', MenuCategoryListCreateView.as_view(), name='menu-category-list-create'),
    path('api/menu-categories/<int:pk>/', MenuCategoryDetailView.as_view(), name='menu-category-detail'),

    # Existing routes
    path('api/tables/<int:pk>/', TableDetailAPIView.as_view(), name='table-detail'),
    path('api/tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
    path('api/contact/', ContactFormSubmissionView.as_view(), name='contact-form-submit'),
    path('api/menu-items/<int:pk>/ingredients/', MenuItemIngredientsView.as_view(), name='menuitem-ingredients'),
    path('api/menu-items/featured/', FeaturedMenuItemsView.as_view(), name='featured-menu-items'),
    path('api/daily-specials/', DailySpecialListView.as_view(), name='daily-specials'),
    # Create a new review
    path('api/reviews/create/', UserReviewCreateAPIView.as_view(), name='review-create'),
    # Get all reviews for a specific menu item
    path('api/menu/<int:menu_item_id>/reviews/', MenuItemReviewsListAPIView.as_view(), name='menuitem-reviews'),
    path('api/menu-categories/', MenuCategoryListView.as_view(), name='menu-categories')
    
]
