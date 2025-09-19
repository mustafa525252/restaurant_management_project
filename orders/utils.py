import secrets
import string

COUPON_CHARACTERS = string.ascii_uppercase + string.digits

def generate_coupon_code(length=10):
    code = ''.join(secrets.choice(COUPON_CHARACTERS) for _ in range(length))
    return code