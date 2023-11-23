from django.contrib import admin
from .models import Pedido

class PedidoAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filtra los pedidos solo para el usuario actual
            qs = qs.filter(user=request.user)
        return qs

admin.site.register(Pedido, PedidoAdmin)