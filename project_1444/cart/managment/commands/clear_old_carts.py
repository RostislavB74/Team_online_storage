import datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from cart.models import Cart


class Command(BaseCommand):
    help = _("Видаляє кошики, які не використовувалися більше 7 днів")

    def handle(self, *args, **kwargs):
        expiration_date = now() - datetime.timedelta(days=7)
        deleted_count, _ = Cart.objects.filter(updated_at__lt=expiration_date).delete()
        self.stdout.write(_("Видалено {} старих кошиків.").format(deleted_count))
