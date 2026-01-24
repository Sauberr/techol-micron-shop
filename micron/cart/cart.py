from decimal import Decimal
from typing import Generator

from django.http import HttpRequest

from coupons.models import Coupon
from django.conf import settings
from products.models import Product


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get("coupon_id")

    def __iter__(self) -> Generator[dict, None, None]:
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]["product"] = product

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            if "bonus_points" in item and item["bonus_points"] is not None:
                item["bonus_points"] = Decimal(item["bonus_points"])
            else:
                item["bonus_points"] = Decimal("0")

            item["total_price"] = item["price"] * item["quantity"]

            if "bonus_points" in item:
                item["total_bonus_points"] = item["bonus_points"] * item["quantity"]

            yield item

    def __len__(self) -> int:
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def coupon(self) -> Coupon | None:
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self) -> Decimal:
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self) -> Decimal:
        return self.get_total_price() - self.get_discount()

    def get_total_price(self) -> int:
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def get_total_bonus_points(self) -> int:
        return sum(
            item["quantity"] * Decimal(item.get("bonus_points", "0") or "0")
            for item in self.cart.values()
        )

    def add(self, product: Product, quantity: int, override_quantity: bool = False) -> None:
        product_id = str(product.id)
        if product_id not in self.cart:
            price = (
                str(product.price_with_discount)
                if product.price_with_discount
                else str(product.price)
            )

            bonus_points = str(
                product.bonus_points if product.bonus_points is not None else 0
            )

            self.cart[product_id] = {
                "quantity": 0,
                "price": price,
                "bonus_points": bonus_points,
            }
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self) -> None:
        self.session.modified = True

    def remove(self, product: Product) -> None:
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self) -> None:
        self.cart.clear()
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        if self.coupon_id:
            if "coupon_id" in self.session:
                del self.session["coupon_id"]
            self.coupon_id = None
        self.session.modified = True
