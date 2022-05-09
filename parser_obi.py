import ast
import requests
from bs4 import BeautifulSoup
import fake_useragent
import traceback
import sqlite3
import os
import shutil
import datetime
import multiprocessing


def authentication():
    url = 'https://www.obi.ru/authentication'
    data = {
        "j_username": "gorab41679@ovooovo.com",
        "j_password": "gorab41679@ovooovo.co",
    }

    session.post(url, headers=header, data=data)

    cookies_dict = [
        {"domain": key.domain, "name": key.name, "path": key.path, "value": key.value}
        for key in session.cookies
    ]

    with open("cookies.txt", mode="w") as file:
        file.write(str(cookies_dict))
    return session


def login():
    with open("cookies.txt", mode="r") as file:
        cookies = ast.literal_eval(file.read())

    for cookie in cookies:
        session.cookies.set(**cookie)
    return session


def main():
    try:
        login()
        response = session.get(url_lk, headers=header)
        assert response.url == url_lk
        print("Куки файлы подошли")
    except:
        print("Куки не подошли")
        authentication()
        print("Заново зашел в аккаунт")

    response = requests.get(url_parse, headers=header).text
    soup = BeautifulSoup(response, "lxml")
    products = soup.find_all("url", limit=100)
    input("Погнали? ")
    for product in products:
        url_product = product.find("loc").text
        product_lk = session.get(url_product, headers=header).text
        product_soup = BeautifulSoup(product_lk, "lxml")

        try:
            block = product_soup.find("div", class_="row-fluid grey-bg")
            price = block.find_all("div", class_="span12 span-mobile12")
            previous_price = price[0].find_all("del")[-1].text
            print(url_product)

            currently_price = price[1].find("span", class_="overview__price").text
            print("previous_price", previous_price)
            print("currently_price", currently_price)

            saving = price[0].find("span", class_="saving").text
            print(saving)

            location = product_soup.find("div", class_="marg_t15 overview__available")
            available = location.find("div", class_="flag__body")
            count_available = available.find_all("p")[1].text
            print(count_available)

            title = product_soup.find("section", class_="overview__description span7-half").find("h1").text
            print(title)

   #          cur.execute("""INSERT INTO discount(shop, title, priviously_price, currently_price, profit, available, url)
   # VALUES("OBI", ?, ?, ?, ?, ?, ?);""", [title, previous_price, currently_price, saving, count_available, url_product])
   #          conn.commit()

        except AttributeError as e:
            print("Нет в наличии", url_product)
            pass

        except IndexError as e:
            print("Нет акции", url_product)
            pass

        except:
            print(url_product)
            traceback.print_exc()


def refactor_bd():
    cur.execute("""SELECT url from discount """)
    urls = cur.fetchall()
    query = """UPDATE discount set id = ? where url = ?"""
    for url in urls:
        idd = url[0].split("/")[-1]
        cur.execute(query, (idd, url[0]))
        conn.commit()


def download_photo():
    cur.execute("""SELECT url, id from discount """)
    urls = cur.fetchall()
    for url in urls:
        print(url[0])
        if os.path.isdir(f"products/{url[1]}"):
            shutil.rmtree(f'products/{url[1]}', ignore_errors=True)
            print("Папка очищена")
        os.mkdir(f"products/{url[1]}")
        print("Папка создана")

        response = requests.get(url[0], headers=header).text
        soup = BeautifulSoup(response, "lxml")
        other = soup.find_all("div", class_="ads-previewslider__item")
        for photo in enumerate(other, start=0):
            url_photo = photo[1].find("img").get("data-lazy")
            image_bytes = requests.get(f"https:{url_photo}").content

            with open(f"products/{url[1]}/{photo[0]}.jpg", mode='wb') as file:
                file.write(image_bytes)
            print("Фотография сохранена")


def tranfer_bd():
    cur.execute("""SELECT * from discount""")
    data = cur.fetchall()
    cur.close()
    conn.close()

    conn2 = sqlite3.connect(r'../debutant_django/db.sqlite3')
    cur2 = conn2.cursor()

    for item in data:
        previous_price = float('.'.join("".join(item[2].split()[:-1]).split(",")))
        currently_price = float('.'.join("".join(item[3].split()[:-1]).split(",")))
        profit = round(previous_price - currently_price, 2)
        slug = f"1-{item[-1]}"
        request = [item[1], previous_price, currently_price, profit, item[5], item[6], slug,
                   datetime.datetime.now(), 1, item[-1]]
        cur2.execute("""
                INSERT INTO discounts_discounts(
                title, previous_price, current_price,
                profit, available, url, slug, created_at,
                shop_id, id_product) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", request)
        conn2.commit()
    cur2.close()
    conn2.close()


def path_photo():
    conn = sqlite3.connect(r'../debutant_django/db.sqlite3')
    cur = conn.cursor()

    path = r"C:\Users\lisgl\Desktop\PycharmProjects\debutant_django\media\products\ОБИ"
    for dirs, folder, files in os.walk(path):
        print('\n')
        for i in files:
            idd = dirs.split('\\')[-1]
            short = '/'.join(dirs.split('\\')[-3:])
            short = f"{short}/{i}"
            cur.execute("""SELECT id from discounts_discounts WHERE id_product=?""", (idd,))
            foreignkey = cur.fetchone()[0]
            cur.execute("""INSERT INTO discounts_photo(image, discount_id) VALUES(?, ?)""", (short, foreignkey))
    conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    url_parse = "https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_877.xml"
    url_lk = "https://www.obi.ru/customer-account"
    session = requests.Session()
    user = fake_useragent.UserAgent().random
    header = {"user-agent": user}
    # conn = sqlite3.connect('obi_discont.db')
    # cur = conn.cursor()

    main()

    # cur.close()
    # conn.close()


# https://www.obi.ru/sitemap_ru.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_876.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_874.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_860.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_877.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_4159.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_875.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_new-products.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_obi-category.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_obi-filtered-category.xml
# https://www.obi.ru/sitemaps/obi_ru_ru/sitemap_obi-search.xml
