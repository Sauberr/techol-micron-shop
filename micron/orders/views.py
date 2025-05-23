import weasyprint
from cart.cart import Cart
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


@login_required(login_url=reverse_lazy("user_account:login"))
def order_create(request):
    cart = Cart(request)

    try:
        shipping = Order.objects.filter(user=request.user.id).latest("created")
    except Order.DoesNotExist:
        shipping = None

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount

            order.bonus_points = cart.get_total_bonus_points()

            order.save()

            for item in cart:

                product = item['product']
                quantity = item['quantity']

                if product.quantity < quantity:
                    messages.error(
                        request,
                        _(
                            "Sorry, only {0} units of {1} are available now. Please update your cart."
                        ).format(product.quantity, product.name),
                    )

                    order.delete()
                    return redirect("cart:cart_summary")

                product.quantity -= quantity
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                    user=request.user,
                )
            cart.clear()
            order_created.delay(order.id)
            request.session["order_id"] = order.id
            return redirect(reverse("payment:process"))
    else:
        if shipping:
            form = OrderCreateForm(instance=shipping)
        else:
            form = OrderCreateForm()
    return render(request, "orders/order/checkout.html", {"cart": cart, "form": form})


@login_required(login_url=reverse_lazy("user_account:login"))
@staff_member_required
def admin_order_detail(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/orders/order/detail.html", {"order": order})


@login_required(login_url=reverse_lazy("user_account:login"))
@staff_member_required
def admin_order_pdf(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string("orders/order/pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + "/css/pdf.css")]
    )
    return response


@login_required(login_url=reverse_lazy("user_account:login"))
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(
        request, "orders/order/orders.html", {"orders": orders, "title": "| Orders"}
    )


@login_required(login_url=reverse_lazy("user_account:login"))
def delete_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect("orders:orders")


@login_required(login_url=reverse_lazy("user_account:login"))
def detail_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    detail_order = OrderItem.objects.filter(user=request.user, order=order)
    return render(
        request,
        "orders/order/order-detail.html",
        {"detail_order": detail_order, "order": order},
    )
