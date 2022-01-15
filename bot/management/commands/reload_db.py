from django.core.management import BaseCommand
from bot.models import *
from colorama import Fore
import logging

logger = logging.getLogger()


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.all().delete()
        Product.objects.all().delete()

        for product in [
            Product.objects.create(name_external='HQD King', count=100, price=700),
            Product.objects.create(name_external='Leaf', count=78, price=800),
            Product.objects.create(name_external='IZY', count=23, price=479)
        ]:
            product.save()

        logger.warning(Fore.YELLOW + f'Data base reloaded' + Fore.WHITE)