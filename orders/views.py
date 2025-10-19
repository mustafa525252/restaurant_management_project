from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Coupon
from rest_framework import generics
from .models import Order
from .serializers import OrderSerializer
# Create your views here.

class CouponValidationView(APIView):
    def post(self, request):
        code = request.data.get('code', '').strip()

        if not code:
            return Response(
                {'error':'Coupon code is requireed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNoeExist:
            return Response(
                {'error':'Invalid coupon code.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        today = timezone.now().date()

        if not coupon.is_active:
            return Response({'error':'This coupon is inactive.'},status=status.HTTP_400_BAD_REQUEST)
        if coupon.valid_form > today:
            return Response({'error':'This coupon is not yet active.'},status=status.HTTP_400_BAD_REQUEST)
        if coupon.valid_until < today:
            return Response({'error':'This coupon has expired.'},status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success':True,
            'code':coupon.code,
            'discount_percentage':float(coupon.discount_percentage),
            'message':f'Coupon "{coupon.code}" is valid for {coupon.discount_percentage}% off!'
        },status=status.HTTP_200_OK)
class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'  # URL will include the order ID