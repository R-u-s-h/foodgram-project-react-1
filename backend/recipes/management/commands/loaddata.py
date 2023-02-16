import csv
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        file = open(
            'data/ingredients.json',
            encoding='utf-8'
        )
        data = json.loads(file.read())
        for ingredient in data:
            Ingredient.objects.get_or_create(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit']
            )

        file = open(
            'data/tags.csv',
            encoding='utf-8'
        )
        data = csv.reader(file)
        for tag in data:
            name, color, slug = tag
            Tag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug
            )
        self.stdout.write(self.style.SUCCESS(settings.LOAD_DATA_SUCCESS))
