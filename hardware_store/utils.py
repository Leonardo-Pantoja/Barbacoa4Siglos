from .models import Cart  # Importa aquí para evitar referencia circular

def get_default_cart(user):
    return Cart.objects.create(user=user)