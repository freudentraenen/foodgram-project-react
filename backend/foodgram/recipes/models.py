from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

import users.models as u_models


class Tag(models.Model):
    name = models.CharField(
        'название',
        max_length=200,
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'цвет',
        default='#000000',
        max_length=7,
        unique=True,
        validators=(
            RegexValidator(
                r'^#(?:[0-9a-fA-F]{3}){1,2}$'
            ),
        )
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        'название рецепта',
        max_length=200
    )
    text = models.TextField(
        'текст рецепта',
        max_length=2000
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    author = models.ForeignKey(
        u_models.User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='тег'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='изображение',
        help_text='добавьте изображение',
        blank=True,
        null=True
    )
    cooking_time = models.PositiveIntegerField(
        'время приготовления',
        validators=(MinValueValidator(1, 'значение должно быть больше 1'),)
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.name

    def get_tags(self) -> str:
        return ',\n'.join([t.name for t in self.tags.all()])
    get_tags.short_description = 'теги'

    def get_ingredients(self) -> str:
        return ',\n'.join(
            [(f'{i.ingredient.name} {str(i.amount)}'
             f' {i.ingredient.measurement_unit}')
             for i in self.ingredients.all()]
        )
    get_ingredients.short_description = 'ингредиенты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='amounts',
        verbose_name='ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'количество',
        validators=(MinValueValidator(1, 'значение должно быть больше 1'),),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'количество ингредиента'
        verbose_name_plural = 'количества ингредиента'

    def __str__(self) -> str:
        return f'Рецепт - {self.recipe}, {self.ingredient} {self.amount}'
