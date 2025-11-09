from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order


@receiver(post_save, sender=Order)
def send_order_status_change_notification(sender, instance, created, **kwargs):
    """
    Sends an email notification to the restaurant admin when an order's status changes.
    """

    # Skip email when order is first created
    if created:
        return

    # Ensure order_status exists before sending
    if not instance.order_status:
        return

    subject = f"Order #{instance.order_id} Status Updated"
    message = (
        f"Dear Admin,\n\n"
        f"The status of order #{instance.order_id} has been updated.\n\n"
        f"New Status: {instance.order_status.name}\n"
        f"Customer: {instance.customer.username}\n"
        f"Order Total: ₹{instance.price * instance.quantity}\n\n"
        f"Please take necessary actions.\n\n"
        f"Best regards,\nRestaurant System"
    )

    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    if not admin_email:
        admin_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending order status email: {e}")
