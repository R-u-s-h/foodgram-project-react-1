import re

from rest_framework.exceptions import ValidationError

from foodgram.settings import WRONG_SYMBOLS, WRONG_USERNAME


def username_validator(value):
    if value == 'me':
        raise ValidationError(WRONG_USERNAME)
    if not re.fullmatch(r'^[\w.@+-]+', value):
        raise ValidationError(
            WRONG_SYMBOLS.format(
                "".join(set(re.findall(r'[^\w.@+-]', value)))
            )
        )
    return value
