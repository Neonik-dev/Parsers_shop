import sqlite3
import traceback
import fake_useragent
import os
import shutil


# path_bd = "obi_discont.db"
path_bd = r"C:\Users\lisgl\Desktop\PycharmProjects\debutant_django\db.sqlite3"
user = fake_useragent.UserAgent().random
header = {"user-agent": user}
isert_discount = """INSERT INTO discounts_discounts(
        title, previous_price, current_price, profit, available, 
        url, slug, created_at, shop_id, id_product) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

select_id_discount = """SELECT id from discounts_discounts WHERE id_product=?"""

insert_photo = """INSERT INTO discounts_photo(image, discount_id) VALUES(?, ?)"""

delete_id_discount = """DELETE FROM discounts_discounts WHERE id_product = ?"""


def clear_bd(shop, path_products):
    conn = sqlite3.connect(path_bd)
    cur = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        cur.execute("""DELETE FROM discounts_discounts WHERE shop_id = ?""", (shop,))
        # cur.execute("""DELETE FROM photo  WHERE shop_id = ?""", (shop,))
        conn.commit()
        if os.path.isdir(f"{path_products}"):
            shutil.rmtree(f'{path_products}', ignore_errors=True)
        os.mkdir(f"{path_products}")
        print("Все данные магазина удалены")
    except Exception:
        traceback.print_exc()
    cur.close()
    conn.close()
