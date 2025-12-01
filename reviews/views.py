from rest_framework import generics
from .models import (
    Review,
    Feedback,
)
from .serializers import (
    ReviewSerializer,
    FeedbackSerializer
)
from .pagination import (
    ReviewPagination
)

class ReviewListView(generics.ListAPIView):
    """
    API endpoint that returns paginated list of restaurant reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = ReviewPagination
    
    
class FeedbackListAPIView(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer