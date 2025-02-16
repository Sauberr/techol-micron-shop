from products.models import Category


def categories(request):
    all_categories = Category.objects.all()
    return {"all_categories": all_categories}
