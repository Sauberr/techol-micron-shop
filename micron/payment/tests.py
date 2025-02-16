from abc import ABC
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class BaseViewTestCase(ABC, TestCase):
    path_name = None
    template_name = None
    title = None

    def setUp(self):
        self.path = reverse(self.path_name) if self.path_name is not None else None

    def test_get(self):
        if self.path is not None:
            response = self.client.get(self.path)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.context['title'], self.title)
            self.assertTemplateUsed(response, self.template_name)


class PaymentSuccessViewTestCase(BaseViewTestCase):
    path_name = 'payment:completed'
    template_name = 'payment/completed.html'
    title = 'Payment Success'


class PaymentCanceledViewTestCase(BaseViewTestCase):
    path_name = 'payment:canceled'
    template_name = 'payment/canceled.html'
    title = 'Payment Canceled'
