import re

from django.core.exceptions import ValidationError


def validate_hex_code(value):
    valid = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value)
    if not valid:
        raise ValidationError('цвет должен быть указан в HEX-формате')


def validate_username(value):
    valid = re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value)
    if not valid:
        raise ValidationError('некорректное имя пользователя')
