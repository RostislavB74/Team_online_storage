# discounts/utils.py
from django.utils.timezone import now
from discounts.models import Discount
from decimal import Decimal
def get_user_available_discounts(user):
    from discounts.models import Discount

    if not user.is_authenticated:
        return []

    now_ = now()
    discounts = Discount.objects.filter(
        user=user,
        is_active=True,
        valid_from__lte=now_,
        valid_to__gte=now_,
        manual_activation=True
    )

    return [d for d in discounts if d.is_valid(user)]

def get_applicable_discounts(product, user=None):
    now_ = now()
    discounts = Discount.objects.filter(
        is_active=True,
        valid_from__lte=now_,
        valid_to__gte=now_,
    ).order_by('-priority')

    applicable = []
    for discount in discounts:
        if product in discount.products.all() or \
           product.category in discount.categories.all() or \
           (user and discount.user == user):
            applicable.append(discount)
    return applicable

