from django.conf.urls import url
from . import views

urlpatterns = [
    url("^$", views.index, name="index"),
    url("^login/$", views.user_login, name="user_login"),
    url("^logout/$", views.user_logout, name="user_logout"),
    url("^register/$", views.register, name="register"),
    url("^contact-us/$", views.contact_us, name="contact_us"),
    url("^shopping-list/$", views.shopping_list, name="shopping_list"),
    url("^shopping-list/add-item/$", views.shopping_list_add_item, name="shopping_list_add_item"),
    url("^products/$", views.products, name="products"),
    url("^recipes/$", views.recipes, name="recipes"),
    url("^recipes/find-recipes/$", views.find_recipes, name="find_recipes"),
    url("^recipes/recipe/$", views.recipe, name="recipe"),
]
