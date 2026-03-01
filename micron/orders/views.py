import weasyprint
from django.db import transaction

from cart.cart import Cart
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import OrderCreateForm
from orders.models.order import Order
from orders.models.order_item import OrderItem
from .tasks import order_created_email, order_created_telegram


@login_required(login_url=reverse_lazy("user_account:login"))
def order_create(request: HttpRequest):
    """Create new order from cart items with stock validation."""
    cart = Cart(request)

    try:
        shipping = Order.objects.filter(user=request.user.id).latest("created_at")
    except Order.DoesNotExist:
        shipping = None

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    if cart.coupon:
                        order.coupon = cart.coupon
                        order.discount = cart.coupon.discount

                    order.bonus_points = cart.get_total_bonus_points()
                    order.save()

                    for item in cart:
                        product = item["product"]
                        quantity = item["quantity"]

                        if product.quantity < quantity:
                            messages.error(
                                request,
                                _(
                                    "Sorry, only {0} units of {1} are available now. Please update your cart."
                                ).format(product.quantity, product.name),
                            )
                            raise ValueError(_("Insufficient product quantity"))

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
                order_created_email.delay(order.id)
                order_created_telegram.delay(order.id)
                request.session["order_id"] = order.id
                return redirect(reverse("payment:process"))

            except (ValueError, Exception):
                messages.error(
                    request, _("An error occurred while processing your order.")
                )
                return redirect("cart:cart_summary")
    else:
        if shipping:
            form = OrderCreateForm(instance=shipping)
        else:
            form = OrderCreateForm()

    return render(request, "orders/order/checkout.html", {"cart": cart, "form": form})


@login_required(login_url=reverse_lazy("user_account:login"))
@staff_member_required
def admin_order_detail(request: HttpRequest, order_id: int):
    """Display order details in admin panel (staff only)."""
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product").select_related("coupon"),
        id=order_id,
    )
    return render(request, "admin/orders/order/detail.html", {"order": order})


@login_required(login_url=reverse_lazy("user_account:login"))
@staff_member_required
def admin_order_pdf(request: HttpRequest, order_id: int):
    """Generate PDF invoice for order (staff only)."""
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product").select_related("coupon"),
        id=order_id,
    )
    html = render_to_string("orders/order/pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + "/css/pdf.css")]
    )
    return response


@login_required(login_url=reverse_lazy("user_account:login"))
def orders(request: HttpRequest):
    """Display list of user orders sorted by date."""
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("items__product")
        .select_related("coupon")
    )
    return render(
        request, "orders/order/orders.html", {"orders": orders, "title": "| Orders"}
    )


@login_required(login_url=reverse_lazy("user_account:login"))
def delete_order(request: HttpRequest, order_id: int):
    """Delete user order by ID."""
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect("orders:orders")


@login_required(login_url=reverse_lazy("user_account:login"))
def detail_order(request: HttpRequest, order_id: int):
    """Display detailed order information with items."""
    order = get_object_or_404(
        Order.objects.select_related("coupon"),
        id=order_id,
        user=request.user,
    )
    detail_order = (
        OrderItem.objects
        .filter(user=request.user, order=order)
        .select_related("product", "user")
    )
    return render(
        request,
        "orders/order/order-detail.html",
        {"detail_order": detail_order, "order": order},
    )
