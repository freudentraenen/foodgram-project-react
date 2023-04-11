from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'get_tags',
        'get_ingredients',
        'image',
        'cooking_time',
        'pub_date'
    )
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'color'
    )
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('recipe', 'ingredient',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.unregister(Group)
