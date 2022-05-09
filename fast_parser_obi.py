import os
import requests
from bs4 import BeautifulSoup
import traceback
import sqlite3
import multiprocessing
import datetime
import general

path_products = "C:/Users/lisgl/Desktop/PycharmProjects/debutant/products/ОБИ"
short_path = "products/ОБИ"
OBI = '1'
urls_parse = ["https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_876.xml",
              "https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_874.xml",
              "https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_877.xml",
              "https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_860.xml",
              "https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_4159.xml",
              "https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_875.xml"]
session = requests.Session()
session.get(
    "https://www.obi.ru/store/change?storeID=008&redirectUrl=https%3A%2F%2Fwww.obi.ru%2Fcustomer-account%2Fstore%23",
    headers=general.header)
conn = sqlite3.connect(general.path_bd)
cur = conn.cursor()
conn.execute("PRAGMA foreign_keys = ON")


def work(product):
    url_product = product[5:-6]
    product_lk = session.get(url_product, headers=general.header).text
    product_soup = BeautifulSoup(product_lk, "lxml")

    try:
        block = product_soup.find("div", class_="row-fluid grey-bg")
        price = block.find_all("div", class_="span12 span-mobile12")
        previous_price = price[0].find_all("del")[-1].text
        currently_price = price[1].find("span", class_="overview__price").text
        print(url_product)

        previous_price = float('.'.join("".join(previous_price.split()[:-1]).split(",")))
        currently_price = float('.'.join("".join(currently_price.split()[:-1]).split(",")))
        profit = round(previous_price - currently_price, 2)
        print("previous_price", previous_price)
        print("currently_price", currently_price)
        print("profit", profit)

        location = product_soup.find("div", class_="marg_t15 overview__available")
        available = location.find("div", class_="flag__body")
        count_available = available.find_all("p")[1].text
        print(count_available)

        title = product_soup.find("section", class_="overview__description span7-half").find("h1").text
        print(title)

        id_product = url_product.split("/")[-1]
        slug = f"{OBI}-{id_product}"

        other = product_soup.find_all("div", class_="ads-previewslider__item")

        data = (title, previous_price, currently_price, profit, count_available,
                url_product, slug, datetime.datetime.now(), OBI, id_product)
        cur.execute(general.isert_discount, data)
        conn.commit()

        try:
            cur.execute(general.select_id_discount, (id_product,))
            foreignkey = cur.fetchone()[0]

            os.mkdir(f"{path_products}/{id_product}")
            print("Папка создана")

            for photo in enumerate(other, start=0):
                url_photo = photo[1].find("img").get("data-lazy").replace("100x75", "415x415")
                print(url_photo)
                image_bytes = requests.get(f"https:{url_photo}").content

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

        except Exception:
            traceback.print_exc()
            cur.execute(general.delete_id_discount, (id_product,))
            conn.commit()
            print("Данные акции удаляются...")

    except AttributeError:
        print("Нет в наличии", url_product)
        pass

    except IndexError:
        print("Нет акции", url_product)
        pass

    except:
        print(url_product)
        traceback.print_exc()


def main():
    try:
        for url_parse in urls_parse:
            response = requests.get(url_parse, headers=general.header).text
            soup = BeautifulSoup(response, "lxml")
            products = list(map(str, soup.find_all("loc")))
            print("Запускаю мультипроцессинг")
            with multiprocessing.Pool(multiprocessing.cpu_count()) as process:
                process.map(work, products)
            print(f"Спарсил {url_parse}")
    except:
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    input("Вы действительно хотите удалить ВСЕ данные ОБИ с базы данных? ")
    general.clear_bd(OBI, path_products)
    main()
