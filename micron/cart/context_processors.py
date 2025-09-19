from django.http import HttpRequest

from .cart import Cart


def cart(request: HttpRequest) -> dict:
    return {"cart": Cart(request)}
