import os
import requests
from bs4 import BeautifulSoup
import traceback
import sqlite3
import multiprocessing
import datetime
import general
url = "https://kazan.megastroy.com/catalog/dekorativnye-oboi"

session = requests.Session()
response = session.get(url, headers=general.header).text
soup = BeautifulSoup(response, 'lxml')
print(len(soup.find_all("div", class_="col-lg-3 col-sm-4 col-xs-6")))

# cookies_dict = [
#     {"domain": key.domain, "name": key.name, "path": key.path, "value": key.value}
#     for key in session.cookies
# ]
cookies_dict = [{"domain": ".megastroy.com", "name": "ipp", "path": "/", "value": "1000"}]

print(*cookies_dict)
session2 = requests.Session()
for cookies in cookies_dict:
    session2.cookies.set(**cookies)

response = session2.get("https://kazan.megastroy.com/catalog/rubanki", headers=general.header).text
soup = BeautifulSoup(response, 'lxml')
print(len(soup.find_all("div", class_="col-lg-3 col-sm-4 col-xs-6")))

for key in session2.cookies:
    print(key.domain, key.name, key.path, key.value)
print(int(soup.find("div", class_="nav-pages clearfix").find("span").text.split()[-1]))