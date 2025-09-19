import secrets
import string

COUPON_CHARACTERS = string.ascii_uppercase + string.digits

def generate_unique_coupon_code(length=10):
    coupon_code = ''.join(secrets.choice(COUPON_CHARACTERS) for _ in range(length))
    return coupon_code