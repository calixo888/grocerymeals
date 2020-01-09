from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib import messages
from . import models
import requests

def index(request):
    return render(request, "grocerymeals_app/index.html", context={
        "index": True,
    })


def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Name processing
        name_list = name.split()
        first_name = None
        last_name = None
        first_name = name_list[0]
        if len(name_list) == 1: # Name is one word (Calix)
            pass
        elif len(name_list) == 2: # Name two words (Calix Huang)
            last_name = name_list[1]
        else: # Name three words or more (Calix boi Huang)
            last_name = " ".join(name_list[1:])

        print(first_name)
        print(last_name)
        print(email)
        print(username)
        print(password)

        user = User(first_name=first_name, last_name=last_name, email=email, username=username)
        user.set_password(password)
        user.save()

        login(request, user)

        return HttpResponseRedirect("/")

    return render(request, "grocerymeals_app/register.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)

                return HttpResponseRedirect("/")
            else:
                messages.success(request, "Your account has be deactivated. Please re-register.")
        else:
            messages.success(request, "Invalid credentials. Please try again.")

    return render(request, "grocerymeals_app/login.html")


@login_required(login_url="/login/")
def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/")


def contact_us(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        EmailMessage("GroceryMeals - Customer Contact", "From: " + name + "\n\n" + message + "\n\nReply To: " + email, to=["calix.huang1@gmail.com"]).send()

        return HttpResponseRedirect("/")

    return render(request, "grocerymeals_app/contact_us.html")


def shopping_list(request):
    products = []
    for item in models.ShoppingListItem.objects.filter(user_id=request.user.id):
        product = models.Product.objects.get(id=item.product_id)
        products.append(product)

    return render(request, "grocerymeals_app/shopping_list.html", context={
        "products": products,
    })


def products(request):
    # Grabbing all products from database
    products = models.Product.objects.all()

    # Redirecting to products if searched
    if request.method == "POST":
        product_name = request.POST.get("product")
        return HttpResponseRedirect("/products/?q=" + product_name)

    # Overwriting products if searched
    query = None
    if request.GET.get("q"):
        query = request.GET.get("q")
        products = models.Product.objects.raw(f"SELECT * FROM grocerymeals_app_product WHERE title LIKE '%{query}%'")

    return render(request, "grocerymeals_app/products.html", context={
        "products": products,
        "query": query,

    })


def recipes(request):
    # Getting ingredients entered and redirecting to search results page
    if request.method == "POST":
        ingredients = request.POST.get("ingredients")

        ingredients = ",+".join(ingredients.split())

        return HttpResponseRedirect("/recipes/find-recipes/?ingredients=" + ingredients)

    return render(request, "grocerymeals_app/recipes.html")


def find_recipes(request):
    # Grabbing ingredients from query parameters
    ingredients = request.GET.get("ingredients")

    # Grabbing 10 recipes with specified ingredients
    recipes = requests.get("https://api.spoonacular.com/recipes/findByIngredients?apiKey=6c61ed1e95de410b845963343f01e258&ingredients=" + ingredients)
    data = recipes.json()

    # Formatting/getting necessary recipe data
    recipes = []
    for recipe_data in data:
        recipe = {
            "image_url": recipe_data["image"],
            "id": recipe_data["id"],
            "title": recipe_data["title"],
        }
        recipes.append(recipe)

    return render(request, "grocerymeals_app/find_recipes.html", context={
        "recipes": recipes,
        "ingredients": ingredients,
    })


def recipe(request):
    # Grabbing recipe ID from query parameters
    id = request.GET.get("id")

    # Grabbing basic recipe information
    info_response = requests.get(f"https://api.spoonacular.com/recipes/{id}/information?apiKey=6c61ed1e95de410b845963343f01e258")
    info_data = info_response.json()

    # Setting variables for template tagging
    image_url = info_data["image"]
    title = info_data["title"]


    # Getting ingredients associated with recipe
    ingredient_response = requests.get(f"https://api.spoonacular.com/recipes/{id}/ingredientWidget.json?apiKey=6c61ed1e95de410b845963343f01e258")
    ingredient_data = ingredient_response.json()

    # Formatting ingredients returned from API
    ingredients = []
    for ingredient in ingredient_data["ingredients"]:
        ingredients.append({
            "name": ingredient["name"],
            "amount": ingredient["amount"]["metric"]["value"],
            "metric": ingredient["amount"]["metric"]["unit"]
        })


    # Getting instructions for recipe
    instructions_response = requests.get(f"https://api.spoonacular.com/recipes/{id}/analyzedInstructions?apiKey=6c61ed1e95de410b845963343f01e258")
    instructions_data = instructions_response.json()

    if instructions_data:
        # Formatting instructions
        instructions = []
        for instruction in instructions_data[0]["steps"]:
            instructions.append(instruction["step"])
    else:
        # No analyzed instructions
        instructions = None

    return render(request, "grocerymeals_app/recipe.html", context={
        "image_url": image_url,
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
    })


# POST REQUESTS

def shopping_list_add_item(request):
    id = request.GET.get("id")

    product = models.Product.objects.get(id=id)

    list_item = models.ShoppingListItem(user_id=request.user.id, product_id=id)
    list_item.save()

    return HttpResponseRedirect("/shopping-list/")
