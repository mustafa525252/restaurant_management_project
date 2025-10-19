
import secrets
import string

COUPON_CHARACTERS = string.ascii_uppercase + string.digits

def generate_unique_coupon_code(length=10):
    coupon_code = ''.join(secrets.choice(COUPON_CHARACTERS)for _ in range(length))
    return coupon_code


def get_daily_sales_total(date):
    orders = Order.objects.filter(created_at__date=date)
    total = orders.aggregate(total_sum=Sum('total_price'))['total_sum']
    return total or 0