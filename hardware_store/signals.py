from django.db.models.signals import post_save
from django.dispatch import receiver

# Crea un carrito para un nuevo usuario
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Client.objects.create(user=instance).create_cart()
