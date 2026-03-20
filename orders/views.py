
from django.views.generic import ListView
from django.contrib.auth.models import User
from .models import Order

class OrderListView(ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.select_related('user').all().order_by('-created_at')
