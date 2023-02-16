from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=settings.TEXT_MAX_LENGTH,
        unique=True,
        validators=[username_validator],
        db_index=True
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.TEXT_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.TEXT_MAX_LENGTH,
        blank=True
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.TEXT_MAX_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка',
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                name='Проверка самоподписки',
                check=~models.Q(user=models.F('author'))),
            models.UniqueConstraint(
                name='Проверка единственности подписки',
                fields=['user', 'author'],)
        ]
