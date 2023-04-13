import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    data_dir = '/app/data/'
    filename = 'ingredients.csv'

    def handle(self, *args, **options) -> None:
        ingredients = []
        with open((self.data_dir + self.filename), encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ingredient = Ingredient(**row)
                ingredients.append(ingredient)
            Ingredient.objects.bulk_create(ingredients)
