from .views import MenuCategoryListView, TableDetailAPIView,AvailableTablesAPIView,ContactFormSubmissionView, MenuItemIngredientsView, FeaturedMenuItemsView
from django.urls import path

urlpatterns = [
    path('menu-categories/',MenuCategoryListView.as_view(),name='menu-categories'),
    path('api/tables/<int:pk>/', TableDetailAPIView.as_view(),name='table-detail'),
    path('api/tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
    path('api/contact/', ContactFormSubmissionView.as_view(), name='contact-form-submit'),
    path('api/menu-items/<int:pk>/ingredients/', MenuItemIngredientsView.as_view(), name='menuitem-ingredients'),
    path('api/menu-items/featured/', FeaturedMenuItemsView.as_view(), name='featured-menu-items'),
]
