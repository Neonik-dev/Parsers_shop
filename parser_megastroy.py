import os
import requests
from bs4 import BeautifulSoup
import traceback
import sqlite3
import multiprocessing
import datetime
import general

path_products = r"C:\Users\lisgl\Desktop\PycharmProjects\debutant_django\media\products\MEGASTROY"
short_path = "products/MEGASTROY"
MEGASTROY = '4'

main_url = "https://kazan.megastroy.com"
cookies_dict = {"domain": ".megastroy.com", "name": "ipp", "path": "/", "value": "1000"}
session = requests.Session()
session.cookies.set(**cookies_dict)

conn = sqlite3.connect(general.path_bd)
cur = conn.cursor()
conn.execute("PRAGMA foreign_keys = ON")


def get_category_urls():
    main_response = requests.get(main_url, headers=general.header).text
    main_soup = BeautifulSoup(main_response, 'lxml')

    hrefs = main_soup.find("div", class_="js-cat-drop hidden-xs")
    urls_category = []

    for item in hrefs:
        levl2 = item.find_all("li")
        for i in levl2:
            urls_category.append(main_url + i.find("a").get("href"))
    return urls_category


def main():
    urls_category = get_category_urls()
    for url in urls_category:
        # url = "https://kazan.megastroy.com/catalog/plitka-dlya-vannoy?products="
        url = f"{url}?products="
        try:
            response = session.get(url, headers=general.header).text
            soup = BeautifulSoup(response, "lxml")
            last_page = 1
            if soup.find("div", class_="nav-pages clearfix"):
                last_page = int(soup.find("div", class_="nav-pages clearfix").find("span").text.split()[-1])
            print(url)

            for page_number in range(1, last_page + 1):
                block_products = soup.find("div", class_="product-list")
                products = block_products.find_all("div", class_="col-lg-3 col-sm-4 col-xs-6")
                print(len(products))
                for item in products:
                    if item.find("div", class_="striked-price"):
                        title = item.find("a", class_="title").get("title")
                        url_product = main_url + item.find("a", class_="title").get("href")
                        print(url_product)
                        try:
                            response_lk = session.get(url_product, headers=general.header).text
                            soup_lk = BeautifulSoup(response_lk, "lxml")
                            block_lk = soup_lk.find("div", class_="product")

                            id_product = block_lk.find("span", "js-codelink").text
                            print(id_product)

                            currently_price = float(block_lk.find("b", itemprop="price").text.replace(" ", ""))
                            print(currently_price)

                            previous_price = float(block_lk.find("div", class_="striked-price").find("b").text.replace(" ", ""))
                            print(previous_price)

                            profit = round(previous_price - currently_price, 2)
                            print(profit)

                            shops = soup_lk.find("div", class_="tab rest-markets").find_all("div", class_="dotted")
                            count_available = 0
                            for available in shops[:4]:
                                try:
                                    count_available += int("".join(available.find_all("span")[-1].text.split()[:-1]))
                                except ValueError:
                                    count_available += int("".join(available.find_all("span")[-1].text.split()[:-2]))
                            print(count_available)

                            slug = f"{MEGASTROY}-{id_product}"

                            os.mkdir(f"{path_products}/{id_product}")
                            print("Папка создана")
                            images = soup_lk.find("div", class_="view").find_all("a", class_="js-abimage")

                            data = (title, previous_price, currently_price, profit, count_available,
                                    url_product, slug, datetime.datetime.now(), MEGASTROY, id_product)
                            cur.execute(general.isert_discount, data)
                            conn.commit()

                            try:
                                cur.execute(general.select_id_discount, (id_product,))
                                foreignkey = cur.fetchone()[0]

                                for photo in enumerate(images, start=0):
                                    url_photo = main_url + photo[1].get("href")
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
                            print("ERROR_LK", url_product)

                if page_number != last_page:
                    response = session.get(f"{url}&page={page_number}", headers=general.header).text
                    soup = BeautifulSoup(response, "lxml")
        except:
            traceback.print_exc()
            print("ERROR", url)


if __name__ == '__main__':
    input("Вы действительно хотите удалить ВСЕ данные МЕГАСТРОЯ с базы данных? ")
    general.clear_bd(MEGASTROY, path_products)
    main()

    cur.close()
    conn.close()
