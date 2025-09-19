


from orders.models import Coupon # Make sure you have Coupon model
import string
import secrets

def generate_coupon_code(length=10):
    characters = string.ascii_uppercase + string.digits

    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))

        if not Coupon.objects.filter(code=code).exists():
            return code