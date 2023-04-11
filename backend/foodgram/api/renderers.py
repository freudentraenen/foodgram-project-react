import io
from rest_framework import renderers

SHOPPING_CART_HEADERS = ['name', 'amount', 'measurement_unit']


class TextDataRenderer(renderers.BaseRenderer):

    media_type = "text/plain"
    format = "txt"

    def render(self, data, accepted_media_type=None, renderer_context=None):

        text_buffer = io.StringIO()
        text_buffer.write(
            ' '.join(header for header in SHOPPING_CART_HEADERS) + '\n')

        for ingredient in data:
            values = []
            name = ingredient['name']
            amount = ingredient['amount']
            measurement_unit = ingredient['measurement_unit']
            values.append(name)
            values.append(amount)
            values.append(measurement_unit)
            text_buffer.write(' '.join(str(value) for value in values) + '\n')

        return text_buffer.getvalue()
