import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import datetime
import multiprocessing
import traceback
import general

path_products = r"C:\Users\lisgl\Desktop\PycharmProjects\debutant_django\media\products\CASTORAMA"
short_path = "products/CASTORAMA"
CASTORAMA = '3'

session = requests.Session()
cookie = {'castorama_current_shop': '51'}
session.get("https://www.castorama.ru", cookies=cookie, headers=general.header)

conn = sqlite3.connect(general.path_bd)
cur = conn.cursor()
conn.execute("PRAGMA foreign_keys = ON")


def cost(price):
    money = price.find("span").find("span")
    penny = money.find("sup")
    money = money.text.replace(" ", "")
    if penny:
        money = ".".join(
            [money[:-len(penny.text)], penny.text])
    money = float(money)
    return money


def work(url):
    print(url)
    url = f"{url}?limit=96"
    response = session.get(url, headers=general.header).text

    while True:
        soup = BeautifulSoup(response, "lxml")
        town = soup.find("span", class_="store-switcher__current-store-i").text.strip()
        if town != "Казань":
            print(f"Город был выбран неверно {town}")
            print(f"-------------- {url} ----------------")
            break

        products = soup.find("div", class_="category-products").find_all("li")
        for item in products:
            try:
                block_price = item.find("div", {"class": "_with-discount"})
                if not block_price:
                    continue
                block_product = item.find("a", class_="product-card__name ga-product-card-name")
                url_product = block_product.get("href")
                title = block_product.get("title")

                page_product = session.get(url_product, headers=general.header).text
                soup_lk = BeautifulSoup(page_product, "lxml")
                block_info = soup_lk.find("div", class_="product-essential__right-col")
                id_product = block_info.find("div", class_="product-essential__sku").find("span").text

                # В товарах может быть указаны цены еще и за упаковку
                price = block_info.find("span", class_="price-suffix")
                try:
                    assert price
                    currently_price = cost(price.find("span", class_="price-per-unit"))
                    previous_price = cost(price.find("span", class_="price"))
                except (AssertionError, AttributeError):
                    price = block_info.find_all("span", class_="price")
                    currently_price = cost(price[0])
                    previous_price = cost(price[1])

                # На сайте имеется баг, который отображет прошлую цену как 0.0
                # Это случается когда товар продают "погонными метрами"
                profit = round(previous_price - currently_price, 2)
                if profit < 0:
                    price = block_info.find("div", class_="price-box") \
                        .find("span", class_="old-price").find("span", class_="price")
                    count = float(block_info.find("input", class_="qty-counter__input input-text qty").get("value"))
                    previous_price = cost(price) / count
                    profit = round(previous_price - currently_price, 2)

                count_available = block_info.find("span", class_="shop _current").find("span",
                                                                                       class_="shop__count").text
                slug = f"{CASTORAMA}-{id_product}"
                print(url_product, title, id_product, previous_price, currently_price, profit, count_available,
                      sep=" | ")

                os.mkdir(f"{path_products}/{id_product}")
                print("Папка создана")
                images = soup_lk.find_all("div", class_="js-zoom-container")

                data = (title, previous_price, currently_price, profit, count_available,
                        url_product, slug, datetime.datetime.now(), CASTORAMA, id_product)
                cur.execute(general.isert_discount, data)
                conn.commit()

                try:
                    cur.execute(general.select_id_discount, (id_product,))
                    foreignkey = cur.fetchone()[0]

                    for photo in enumerate(images, start=0):
                        url_photo = photo[1].find("img").get("data-src")
                        image_bytes = requests.get(url_photo).content
                        with open(f"{path_products}/{id_product}/{photo[0]}.jpg", mode='wb') as file:
                            file.write(image_bytes)
                        cur.execute(general.insert_photo,
                                    (f"{short_path}/{id_product}/{photo[0]}.jpg", foreignkey))
                        conn.commit()

                    if not os.listdir(f"{path_products}/{id_product}"):
                        print("------------------------------------")
                        print(url_product)
                        print("------------------------------------")
                        raise Exception("Ни одно изображение товара не скаченно")

                    print("Фотографии сохранены")
                except:
                    traceback.print_exc()
                    cur.execute(general.delete_id_discount, (id_product,))
                    conn.commit()
                    print("Данные акции удаляются...", url_product)
            except:
                traceback.print_exc()
                print("ERROR", url_product)

        next_page = soup.find("a", class_="next i-next")
        if not next_page:
            break
        page_number = next_page.get("href").split("p=")[-1]
        response = session.get(f"{url}&p={page_number}", headers=general.header).text
        print(f"{url}&p={page_number}")


def main():
    page = requests.get("https://www.castorama.ru/media/sitemap/default/sitemap_category_0_.xml",
                        headers=general.header).text
    soup = BeautifulSoup(page, "lxml")
    urls = soup.find_all("url")
    menu_product = []
    for item in urls:
        url = item.find("loc").text
        number = item.find("priority").text
        if number != "0.9" and url.find("collections") == -1 and url.find("proizvoditeli") == -1 and url.find(
                "legkiy-vybor") == -1:
            menu_product.append(url)
    print(len(menu_product))

    try:
        with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
            process.map(work, menu_product)
    except:
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    input("Вы действительно хотите удалить ВСЕ данные КАСТОРАМЫ с базы данных? ")
    general.clear_bd(CASTORAMA, path_products)
    main()
