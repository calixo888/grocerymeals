from django.conf.urls import url
from . import views

urlpatterns = [
    url("^$", views.index, name="index"),
    url("^products/$", views.products, name="products"),
    url("^recipes/$", views.recipes, name="recipes"),
    url("^recipes/find-recipes/$", views.find_recipes, name="find_recipes"),
    url("^recipes/recipe/$", views.recipe, name="recipe"),
]
