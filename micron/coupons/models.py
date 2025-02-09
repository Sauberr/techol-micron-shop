from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from faker import Faker


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage value (0 to 100)",
    )
    active = models.BooleanField()

    class Meta:
        verbose_name: str = "coupon"
        verbose_name_plural: str = "coupons"

    def __str__(self):
        return self.code

    @classmethod
    def generate_instances(cls, count):
        faker = Faker()
        for _ in range(count):
            cls.objects.create(
                code=faker.name(),
                valid_from=faker.date_time_this_year(),
                valid_to=faker.date_time_this_year(),
                discount=faker.random_int(1, 100),
                active=faker.boolean(),
            )
