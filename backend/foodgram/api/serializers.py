from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient
from users.models import User, Follow


class NestedRecipeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def get_image(self, obj):
        request = self.context['request']
        image_url = obj.image.url
        absolute_url = request.build_absolute_uri(image_url).replace(
            'backend:8000', '127.0.0.1'
        )
        return absolute_url


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    recipes = NestedRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
            'recipes'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        return make_password(value)

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(
                user=self.context['request'].user,
                following=obj
            ).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class NestedIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(min_value=1)

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    ingredient = NestedIngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'ingredient'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        del ret['ingredient']
        ret['id'] = instance.ingredient.pk
        ret['name'] = instance.ingredient.name
        ret['measurement_unit'] = instance.ingredient.measurement_unit
        ret['amount'] = instance.amount
        return ret


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    amount = serializers.IntegerField(min_value=1)


class RecipeFavoritesShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = '__all__'


class RecipeReadSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()

    is_in_shopping_cart = serializers.SerializerMethodField()

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientReadSerializer(many=True)
    author = UserSerializer(
        read_only=True,
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',

        )
        depth = 1

    def get_image(self, obj):
        request = self.context['request']
        image_url = obj.image.url
        absolute_url = request.build_absolute_uri(image_url).replace(
            'backend:8000', '127.0.0.1'
        )
        return absolute_url

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj in self.context['request'].user.favorite_recipes.all()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj in self.context['request'].user.shopping_cart.all()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):

    is_favorited = serializers.SerializerMethodField()

    is_in_shopping_cart = serializers.SerializerMethodField()

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    author = UserSerializer(
        read_only=True,
    )
    image = Base64ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',

        )
        depth = 1

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        objs = []
        for ingredient_data in ingredients_data:
            id = ingredient_data.pop('id')
            amount = ingredient_data.pop('amount')
            obj = RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=id),
                amount=amount
            )
            objs.append(obj)
        RecipeIngredient.objects.bulk_create(objs)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data.keys():
            instance.ingredients.all().delete()
            ingredients_data = validated_data.pop('ingredients')
            objs = []
            for ingredient_data in ingredients_data:
                id = ingredient_data.pop('id')
                amount = ingredient_data.pop('amount')
                obj, _ = RecipeIngredient.objects.get_or_create(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient, pk=id),
                    amount=amount
                )
                objs.append(obj)
            RecipeIngredient.objects.bulk_create(objs, ignore_conflicts=True)
        tags = validated_data.get('tags', instance.tags)
        instance.tags.set(tags)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj in self.context['request'].user.favorite_recipes.all()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj in self.context['request'].user.shopping_cart.all()
        return False
