from django.urls import path
from .views import *

urlpatterns = [
    paht('menu-categories/',MenuCategoryListView.as_view(),name='menu-categories'),
]