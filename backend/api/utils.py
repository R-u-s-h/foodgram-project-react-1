from django.db.models import Sum
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from recipes.models import IngredientRecipe


@staticmethod
def canvas_method(dictionary):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename = "cart.pdf"'
    begin_position_x, begin_position_y = 40, 650
    sheet = canvas.Canvas(response, pagesize=A4)
    pdfmetrics.registerFont(
        TTFont('FreeSans', 'data/FreeSans.ttf')
    )
    sheet.setFont('FreeSans', 36)
    sheet.setTitle('Список покупок')
    sheet.drawString(
        begin_position_x,
        begin_position_y + 40,
        'Список покупок: '
    )
    sheet.setFont('FreeSans', 20)
    for number, item in enumerate(dictionary, start=1):
        if begin_position_y < 100:
            begin_position_y = 700
            sheet.showPage()
            sheet.setFont('FreeSans', 24)
        sheet.drawString(
            begin_position_x,
            begin_position_y,
            f'{number}.  {item["ingredient__name"]} - '
            f'{item["ingredient_total"]}'
            f' {item["ingredient__measurement_unit"]}'
        )
        begin_position_y -= 30
    sheet.showPage()
    sheet.save()
    return response


def download_shopping_cart(request):
    result = IngredientRecipe.objects.filter(
        recipe__cart__user=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).order_by(
        'ingredient__name'
    ).annotate(
        ingredient_total=Sum('amount')
    )
    return canvas_method(result)