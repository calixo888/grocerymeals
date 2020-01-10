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
from selenium import webdriver
import re
from grocerymeals_app import models
import requests
from bs4 import BeautifulSoup

def job():
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

    print("started")

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
        soup = BeautifulSoup(html)
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
        print("added")

schedule.every(1).minutes.do(job)

def interval():
    while True:
        schedule.run_pending()
        time.sleep(1)

# threading.Thread(target=interval).start()
