"""grocerymeals_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('grocerymeals_app.urls')),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Running data-fetching interval
import schedule
import time
import threading
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import re
from grocerymeals_app import models
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

account_sid = 'ACfd9dc8dfdc0bae80dfe05ba0e75af37f'
auth_token = '7209ab86358baa99b15c920ee17a3b86'
client = Client(account_sid, auth_token)

def send_text(message):
    message = client.messages \
        .create(
             body=message,
             from_='+1 925 701 8067',
             to='9253326127'
         )

def check_exists_by_class(class_name):
    try:
        driver.find_element_by_class_name(class_name)
    except NoSuchElementException:
        return False
    return True

def job():
    # Clearing out products table
    models.Product.objects.all().delete()

    # Scraping and storing products from grocers
    send_text("Starting GroceryMeals scraping process...")
    sprouts()
    safeway()
    albertsons()
    smart_and_final()
    whole_foods()

    sent_text("GroceryMeals scraping process complete.")

def sprouts():
    def image_links(soup):
        image_links = []
        regex = re.compile("data-src=\"(.*?)\"")

        for img in soup.find_all("a", attrs={"class": "cell-image"}):
            link = regex.findall(str(img))[0]
            image_links.append(link)

        return image_links

    def titles(soup):
        title_list = []
        regex = re.compile(">(.*)<")

        for text in soup.find_all("span", attrs={"class": "cell-title-text"}):
            title = regex.findall(str(text))[0]
            title_list.append(title)

        return title_list

    def prices(soup):
        price_list = []
        regex = re.compile(">(.*)<")

        price_val_list = []
        metric_val_list = []

        for price in soup.find_all("span", attrs={"class": "css-1733kw7"}):
            price_val_list.append(regex.findall(str(price))[0])

        for metric in soup.find_all("span", attrs={"class": "css-15hnye8"}):
            metric_val_list.append(regex.findall(str(metric))[0])

        for price_pair in zip(price_val_list, metric_val_list):
            price_list.append("".join(price_pair))

        return price_list

    driver = webdriver.Chrome("/Users/calixhuang/Documents/chromedriver")
    url = "https://shop.sprouts.com/shop/categories/2"
    html_list = []

    driver.get(url)
    time.sleep(5)

    html = driver.page_source
    html_list.append(html)

    url += "?page=2"

    driver.get(url)
    time.sleep(5)

    html = driver.page_source
    html_list.append(html)

    driver.close()

    image_links_list = []
    titles_list = []
    price_list = []

    for html in html_list:
        soup = BeautifulSoup(html, "lxml")
        products = soup.find_all("div", attrs={"class": "product-cell"})

        image_links_list.append(image_links(soup))
        titles_list.append(titles(soup))
        price_list.append(prices(soup))

    image_links_list = [j for sub in image_links_list for j in sub]
    titles_list = [j for sub in titles_list for j in sub]
    price_list = [j for sub in price_list for j in sub]

    # Formatting names
    formatted_titles = []
    for name in titles_list:
        name_list = name.split()

        index_counter = 0
        while True:
            if len(name_list) == index_counter:
                break

            word = name_list[index_counter]

            if word.endswith(","):
                name_list[index_counter] = word[:-1]
                index_counter += 1
                break

            if word.startswith("("):
                break

            index_counter += 1

        formatted_name = " ".join(name_list[:index_counter])
        formatted_titles.append(formatted_name)

    for info_bunch in zip(image_links_list, titles_list, formatted_titles, price_list):
        models.Product.objects.create(image_url=info_bunch[0], title=info_bunch[1], provider="Sprouts", formatted_title=info_bunch[2], price=info_bunch[3])


def safeway():
    html = None
    attempts = 0
    driver = webdriver.Chrome("/Users/calixhuang/Documents/chromedriver")

    driver.get("https://www.safeway.com/shop/search-results.html?q=fruits%20and%20vegetables")

    time.sleep(2)

    # Closing cookie consent
    try:
        driver.find_element_by_id("cookieConsentClose").click()
    except:
        pass

    while True:
        if attempts == 3:
            html = driver.page_source
            break

        try:
            load_btn = driver.find_element_by_class_name("bloom-load-button")

            actions = ActionChains(driver)
            actions.move_to_element(load_btn).perform()

            load_btn.click()

            attempts = 0

            time.sleep(2)
        except:
            attempts += 1

    driver.close()


    # Parsing
    soup = BeautifulSoup(html, "lxml")

    products = soup.find_all("div", attrs={"class": "product-grid"})

    images = []
    titles = []
    quantities = []
    prices = []

    for product in products:
        try:
            image = product.find("img", attrs={"ab-lazy"})["src"]
            images.append(image) # Product Image
        except:
            images.append("{% static 'img/no-image.png' %}")

        # Product Title
        title = product.find("a", attrs={"class": "product-title"}).get_text()
        titles.append(title)

        # Product Quantity
        quantity = product.find("span", attrs={"class": "product-price-qty"}).get_text()
        quantities.append(quantity)

        # Product Price
        str_price = product.find("span", attrs={"class": "product-price"}).get_text()
        price = float(str_price.split("$")[1])
        prices.append(price)

    for info_bunch in zip(images, titles, titles, prices):
        models.Product.objects.create(image_url=info_bunch[0], title=info_bunch[1], provider="Safeway", formatted_title=info_bunch[2], price=info_bunch[3])


def albertsons():
    html = None
    attempts = 0
    driver = webdriver.Chrome("/Users/calixhuang/Documents/chromedriver")

    driver.get("https://www.albertsons.com/shop/search-results.html?q=fruits%20and%20vegetables")

    # Closing cookie consent
    try:
        driver.find_element_by_id("cookieConsentClose").click()
    except:
        pass

    while True:
        if attempts == 3:
            html = driver.page_source
            break

        try:
            load_btn = driver.find_element_by_class_name("bloom-load-button")

            actions = ActionChains(driver)
            actions.move_to_element(load_btn).perform()

            load_btn.click()

            attempts = 0

            time.sleep(2)
        except:
            attempts += 1

    driver.close()


    # Parsing
    soup = BeautifulSoup(html, "lxml")

    products = soup.find_all("div", attrs={"class": "product-grid"})

    images = []
    titles = []
    quantities = []
    prices = []

    for product in products:
        try:
            image = product.find("img", attrs={"ab-lazy"})["src"]
            images.append(image) # Product Image
        except:
            images.append("{% static 'img/no-image.png' %}")

        # Product Title
        title = product.find("a", attrs={"class": "product-title"}).get_text()
        titles.append(title)

        # Product Quantity
        quantity = product.find("span", attrs={"class": "product-price-qty"}).get_text()
        quantities.append(quantity)

        # Product Price
        str_price = product.find("span", attrs={"class": "product-price"}).get_text()
        price = float(str_price.split("$")[1])
        prices.append(price)

    for info_bunch in zip(images, titles, titles, prices):
        models.Product.objects.create(image_url=info_bunch[0], title=info_bunch[1], provider="Albertsons", formatted_title=info_bunch[2], price=info_bunch[3])


def smart_and_final():
    html = None
    attempts = 0
    driver = webdriver.Chrome("/Users/calixhuang/Documents/chromedriver")
    page_number = 1
    product = "fruits"
    base_url = f"https://www.smartandfinal.com/shop/?query={product}&page={page_number}&pagesize=96&apply_user_tags=1"

    images = []
    titles = []
    prices = []

    # Selecting closest store
    driver.get(base_url)
    time.sleep(5)
    set_as_closest_store_btn = driver.find_element_by_class_name("set-my-closest-store")
    set_as_closest_store_btn.click()

    for i in range(2):
        while True:
            url = f"https://www.smartandfinal.com/shop/?query={product}&page={page_number}&pagesize=96&apply_user_tags=1"
            driver.get(url)

            time.sleep(3)

            # Checking if this is last page
            if driver.current_url == f"https://www.smartandfinal.com/shop/?query={product}&page=1&pagesize=96&apply_user_tags=1" and page_number > 1:
                break

            soup = BeautifulSoup(driver.page_source, "lxml")

            # Images
            temp_images = [i["src"] if i.has_attr("src") else "Not available" for i in soup.find_all("img", attrs={"class": "item-image"})]
            images.append(temp_images)

            # Titles
            temp_titles = [i.get_text() for i in soup.find_all("span", attrs={"class": "product-name"})]
            titles.append(temp_titles)

            # Prices
            temp_prices = [i.get_text() for i in soup.find_all("div", attrs={"class": "regular-price"})]
            prices.append(temp_prices)

            page_number += 1

        product = "vegetables"
        page_number = 1

    driver.close()

    images = [j for sub in images for j in sub]
    titles = [j for sub in titles for j in sub]
    prices = [j for sub in prices for j in sub]

    for info_bunch in zip(images, titles, titles, prices):
        models.Product.objects.create(image_url=info_bunch[0], title=info_bunch[1], provider="Smart and Final", formatted_title=info_bunch[2], price=info_bunch[3])


def whole_foods():
    images = []
    titles = []
    prices = []

    html = None
    driver = webdriver.Chrome("/Users/calixhuang/Documents/chromedriver")
    page_number = 1
    categories = ["produce"]
    url = f"https://products.wholefoodsmarket.com/search?sort=relevance&store=10126&category={categories[0]}"

    driver.get(url)

    # Selecting a store
    driver.find_element_by_class_name("Dropdown-Root--55pLk").click()
    time.sleep(1)
    driver.find_element_by_class_name("Input-InputField--KUzM1").send_keys("94506")
    time.sleep(1)
    driver.find_element_by_class_name("StoreSelector-Option--mQyct").click()

    for category in categories:
        url = f"https://products.wholefoodsmarket.com/search?sort=relevance&store=10126&category={category}"

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            prev_html = driver.page_source
            time.sleep(2)

            post_html = driver.page_source

            if prev_html == post_html:
                html = driver.page_source
                break

        soup = BeautifulSoup(html, "lxml")

        products = soup.find_all("a", attrs={"class": "ProductCard-Root--3g5WI"})

        temp_images = []
        for image in soup.find_all("div", attrs={"class": "LazyImage-Image--1HP-y"}):
            try:
                temp_images.append(image["style"])
            except:
                temp_images.append("{% static 'img/no-image.png' %}")

        temp_titles = [i.get_text() for i in soup.find_all("div", attrs={"class": "ProductCard-Name--1o2Gg"})]
        temp_prices = [i.get_text() for i in soup.find_all("div", attrs={"class": "ProductCard-Price--1uInW"}) if not i.has_attr("data-dashed")]

        images.append(temp_images)
        titles.append(temp_titles)
        prices.append(temp_prices)

    driver.close()

    images = [j for sub in images for j in sub]
    titles = [j for sub in titles for j in sub]
    prices = [j for sub in prices for j in sub]

    for info_bunch in zip(images, titles, titles, prices):
        models.Product.objects.create(image_url=info_bunch[0], title=info_bunch[1], provider="Whole Foods", formatted_title=info_bunch[2], price=info_bunch[3])

schedule.every(1440).minutes.do(job)

def interval():
    while True:
        schedule.run_pending()
        time.sleep(1)

# threading.Thread(target=interval).start()
