from rest_framework import generics
from .models import Review
from .serializers import ReviewSerializer
from .pagination import ReviewPagination

class ReviewListView(generics.ListAPIView):
    """
    API endpoint that returns paginated list of restaurant reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = ReviewPagination