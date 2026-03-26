from django.urls import path
from .views import OrderListView, OrderListApiView, OrderDetailApiView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('api/orders/', OrderListApiView.as_view(), name='api-order-list'),
    path('api/orders/<int:order_id>/', OrderDetailApiView.as_view(), name='api-order-detail'),
]