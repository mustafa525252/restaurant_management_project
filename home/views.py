from django.shortcuts import render
from rest_framework import generics
from rest_framework.generics import ListAPIView
from .models import MenuCategory,Table
from .serializers import MenuCategorySerializer, TableSerializer

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