from . import models
from django.conf import settings

def add_variable_to_context(request):
    # Getting amount of shopping list items
    number_of_shopping_list_items = None
    if request.user.is_authenticated:
        number_of_shopping_list_items = len(models.ShoppingListItem.objects.filter(user_id=request.user.id))

    return {
        "number_of_shopping_list_items": number_of_shopping_list_items,
        "testing": settings.TESTING,
    }
