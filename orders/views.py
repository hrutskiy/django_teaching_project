import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from .models import Order


class OrderListView(ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.select_related('user').all().order_by('-created_at')


def order_to_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "user_id": order.user_id,
        "username": order.user.username,
        "title": order.title,
        "amount": str(order.amount),
        "status": order.status,
        "is_active": order.is_active,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }


@method_decorator(csrf_exempt, name='dispatch')
class OrderListApiView(View):
    def get(self, request):
        orders = Order.objects.select_related("user").all().order_by("-created_at")
        data = [order_to_dict(order) for order in orders]
        return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user_id = data.get("user_id")
        title = data.get("title")
        amount = data.get("amount")

        if not user_id or not title or amount is None:
            return JsonResponse(
                {"error": "user_id, title, amount are required"},
                status=400,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            return JsonResponse({"error": "Invalid amount"}, status=400)

        order = Order.objects.create(
            user=user,
            title=title,
            amount=amount,
        )

        return JsonResponse(order_to_dict(order), status=201)


@method_decorator(csrf_exempt, name='dispatch')
class OrderDetailApiView(View):
    def get(self, request, order_id):
        try:
            order = Order.objects.select_related("user").get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

        return JsonResponse(order_to_dict(order))

    def put(self, request, order_id):
        try:
            order = Order.objects.select_related("user").get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if "title" in data:
            order.title = data["title"]

        if "amount" in data:
            try:
                order.amount = Decimal(str(data["amount"]))
            except (InvalidOperation, ValueError):
                return JsonResponse({"error": "Invalid amount"}, status=400)

        if "status" in data:
            valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            if data["status"] not in valid_statuses:
                return JsonResponse({"error": "Invalid status"}, status=400)
            order.status = data["status"]

        if "is_active" in data:
            order.is_active = data["is_active"]

        if "user_id" in data:
            try:
                order.user = User.objects.get(id=data["user_id"])
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)

        order.save()
        return JsonResponse(order_to_dict(order))

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

        order.delete()
        return JsonResponse({"message": "Order deleted"})