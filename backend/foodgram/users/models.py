from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    first_name = models.CharField(
        'имя',
        max_length=150
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    username = models.CharField(
        'имя пользователя',
        max_length=150,
        unique=True,
        validators=(
            RegexValidator(
                r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$'
            ),
        )
    )
    password = models.CharField(
        'пароль',
        max_length=150,
        unique=True
    )
    favorite_recipes = models.ManyToManyField(
        'recipes.Recipe',
        related_name='users_who_favorited',
        verbose_name='избранные рецепты',
        blank=True
    )
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        related_name='users_who_shopped',
        verbose_name='список покупок',
        blank=True
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self) -> str:
        return self.username

    def get_favorite_recipes(self) -> str:
        return ',\n'.join([f_r.name for f_r in self.favorite_recipes.all()])
    get_favorite_recipes.short_description = 'избранные рецепты'

    def get_shopping_cart(self) -> str:
        return ',\n'.join([s_r.name for s_r in self.shopping_cart.all()])
    get_shopping_cart.short_description = 'список покупок'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follows',
        verbose_name='подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='тот, на кого подписан'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_followers',
                violation_error_message='Вы уже подписаны на этого пользовтеля'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='no_self_subscribe',
                violation_error_message='Нельзя подписаться на себя'
            )
        )

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.following}'

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)
