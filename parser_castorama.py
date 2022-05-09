import math
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import datetime
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
import general


path_products = "C:/Users/lisgl/Desktop/PycharmProjects/debutant/products/CASTORAMA"
short_path = "products/CASTORAMA"
CASTORAMA = '3'
path = r"C:\Users\lisgl\Desktop\PycharmProjects\geckodriver.exe"
conn = sqlite3.connect(general.path_bd)
cur = conn.cursor()

option = webdriver.FirefoxOptions()
option.set_preference("dom.webdriver.enabled", False)
option.set_preference("dom.webnotification.enabled", False)
option.set_preference("general.useragent.override", general.user)


# option.headless = True


def work(urls):
    browser = webdriver.Firefox(executable_path=path, options=option)
    browser.get("https://www.castorama.ru")
    wait20 = WebDriverWait(browser, 20)
    try:
        time.sleep(10)
        wait20.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div[2]/header/div[2]/div[3]/div/div[2]/span/span"))).click()
        while True:
            try:
                time.sleep(10)
                wait20.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".header-shop-select__i > div:nth-child(2) > ul:nth-child(2) > li:nth-child(5) > span:nth-child(1)"))).click()
                break
            except:
                wait20.until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div[2]/header/div[2]/div[3]/div/div[2]/span/span"))).click()

        # проверка города
        flag = True
        for i in range(10):
            time.sleep(5)
            if browser.find_element_by_xpath(
                    "/html/body/div[1]/div[2]/header/div[2]/div[3]/div/div[2]/span/span").text == "Казань":
                print("Город выбран верно")
                flag = False
                break
        if flag:
            raise AssertionError
    except AssertionError:
        print("Неверно выбран город")
        print(urls)
        browser.close()
        return
    except Exception:
        traceback.print_exc()

    for url_products in urls:
        print(url_products)
        browser.get(f"{url_products}?limit=96")
        while True:
            response = browser.page_source
            soup_product = BeautifulSoup(response, "lxml")
            products = soup_product.find("div", class_="category-products").find_all("li")
            for item in products:
                try:
                    block_price = item.find("div", {"class": "_with-discount"})
                    if not block_price:
                        continue

                    block_product = item.find("a", class_="product-card__name ga-product-card-name")
                    url_product = block_product.get("href")
                    title = block_product.get("title")

                    # print(price[0].text)
                    # print(price[1].text)
                    # previous_price =
                    # previous_price = float('.'.join("".join(price[0].text.split()[:-1]).split(",")))
                    # currently_price = float('.'.join("".join(price[1].text.strip()[:-4]).split(",")))
                    # profit = round(previous_price - currently_price, 2)
                    # print(url_product, title, previous_price, currently_price)

                    page_product = requests.get(url_product).text
                    soup_lk = BeautifulSoup(page_product, "lxml")
                    id_product = soup_lk.find("div", class_="product-essential__sku").find("span").text
                    print(url_product, title, id_product)

                    price = block_price.find("span", class_="price-per-unit")
                    if price:
                        price = price.find("span").find("span")
                        penny = price.find("sup")
                        currently_price = price.text
                        if penny:
                            currently_price = ".".join([currently_price[:-len(penny.text)].replace(" ", ""), penny.text])
                        currently_price = float(currently_price)
                        print(currently_price)


                    else:
                        price = block_price.find_all("span", class_="price")
                        price[0] = price[0].find("span").find("span")
                        penny = price[0].find("sup")
                        currently_price = price[0].text
                        if penny:
                            print("------------------------------------------------------")
                            print(url_product)
                            print("------------------------------------------------------")

                            currently_price = ".".join([currently_price[:-len(penny.text)].replace(" ", ""), penny.text])
                        currently_price = float(currently_price)
                        print(currently_price)

                        price[1] = price[1].find("span").find("span")
                        penny = price[1].find("sup")
                        previous_price = price[1].text
                        if penny:
                            print("------------------------------------------------------")
                            print(url_product)
                            print("------------------------------------------------------")

                            previous_price = ".".join(
                                [previous_price[:-len(penny.text)].replace(" ", ""), penny.text])
                        previous_price = float(previous_price)
                        print(previous_price)

                    # data = (title, previous_price, currently_price)
                    # cur.execute(general.isert_discount, data)
                    # conn.commit()

                    os.mkdir(f"{path_products}/{id_product}")
                    print("Папка создана")
                    other = soup_lk.find_all("div", class_="js-zoom-container")

                    for photo in enumerate(other, start=0):
                        url_photo = photo[1].find("img").get("data-src")
                        print(url_photo)
                        image_bytes = requests.get(url_photo).content

                        with open(f"{path_products}/{id_product}/{photo[0]}.jpg", mode='wb') as file:
                            file.write(image_bytes)
                except Exception:
                    traceback.print_exc()
            next_page = soup_product.find("a", class_="next i-next")
            if not next_page:
                break

            print(next_page.get("href"))
            browser.get(next_page.get("href"))
    browser.close()


def main():
    page = requests.get("https://www.castorama.ru/media/sitemap/default/sitemap_category_0_.xml").text
    soup = BeautifulSoup(page, "lxml")
    urls = soup.find_all("url")
    menu_product = []
    for item in urls:
        url = item.find("loc").text
        number = item.find("priority").text
        if number != "0.9" and url.find("collections") == -1 and url.find("proizvoditeli") == -1 and url.find(
                "legkiy-vybor") == -1:
            menu_product.append(url)

    chunks = []
    length = math.ceil(len(menu_product) / multiprocessing.cpu_count())
    for i in range(multiprocessing.cpu_count() - 1):
        chunks.append(menu_product[i * length: (i + 1) * length])
    chunks.append(menu_product[(multiprocessing.cpu_count() - 1) * length:])

    # with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
    with multiprocessing.Pool(1) as process:
        process.map(work, chunks)

    cur.close()
    conn.close()


if __name__ == '__main__':
    input("Вы действительно хотите удалить ВСЕ данные КАСТОРАМЫ с базы данных? ")
    general.clear_bd(CASTORAMA, path_products)
    main()
