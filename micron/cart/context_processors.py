from django.http import HttpRequest

from .cart import Cart


def cart(request: HttpRequest):
    return {"cart": Cart(request)}
