from .views import MenuCategoryListView, TableDetailAPIView,AvailableTablesAPIView
from django.urls import path

urlpatterns = [
    path('menu-categories/',MenuCategoryListView.as_view(),name='menu-categories'),
    path('api/tables/<int:pk>/', TableDetailAPIView.as_view(),name='table-detail')
    path('api/tables/available/', AvailableTablesAPIView.as_view(), name='available_tables_api'),
]
