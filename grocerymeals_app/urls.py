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
    url("^shopping-list/delete-item/$", views.shopping_list_delete_item, name="shopping_list_delete_item"),
    url("^products/$", views.products, name="products"),
    url("^recipes/$", views.recipes, name="recipes"),
    url("^recipes/find-recipes/$", views.find_recipes, name="find_recipes"),
    url("^recipes/recipe/$", views.recipe, name="recipe"),
    url("^products/product/(?P<product_id>[^/]+)/$", views.product, name="product"),
    url("^terms-of-service/$", views.terms_of_service, name="terms_of_service"),
    url("^privacy-policy/$", views.privacy_policy, name="privacy_policy"),
]
