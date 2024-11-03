from typing import Any, Type

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from payment.models import ShippingAddress

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_shipping_address(
    sender: Type[User], instance: User, created: bool, **kwargs: Any
) -> None:
    """
    Signal handler that creates a default shipping address for a
    user upon account creation, if they don't already have one.
    """
    if created:
        if not ShippingAddress.objects.filter(user=instance).exists():
            ShippingAddress.create_default_shipping_address(user=instance)
