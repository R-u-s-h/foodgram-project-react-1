import json
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        file = open(
            'data/ingredients.json',
            encoding='utf-8'
        )
        data = json.loads(file.read())
        for ingredient in data:
            name = ingredient['name']
            measurement_unit = ingredient['measurement_unit']
            Ingredient.objects.create(
                name=name,
                measurement_unit=measurement_unit
            )
