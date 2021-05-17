import logging
import requests
from bs4 import BeautifulSoup
import csv
import time

CSV = 'dresses.csv'
PAGES = 150
HOST = 'https://www.lamoda.ru'
URL = 'https://www.lamoda.ru/c/369/clothes-platiya/?page=1'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 YaBrowser/20.9.0.933 Yowser/2.5 Safari/537.36'
}


def get_html(url, params=''):
    request = requests.get(url, headers=HEADERS, params=params)
    return request


def get_characteristics(url, params=''):
    characteristic = {}
    request = requests.get(url, headers=HEADERS, params=params)
    soup = BeautifulSoup(request.text, 'html.parser')
    description = soup.find('div', class_='ii-product__description-text')
    labels = [label.get_text(strip=True) for label in description.find_all('span',
                                                                           class_='ii-product__attribute-label')]
    values = [value.get_text(strip=True) for value in description.find_all('span',
                                                                           class_='ii-product__attribute-value')]
    for i in range(len(labels)):
        characteristic[labels[i]] = values[i]
    return characteristic


def get_content(html):
    dresses = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='products-list-item')
    for item in items:
        url_of_item = HOST + item.find('a').get('href')
        characteristics = get_characteristics(url_of_item)
        dresses.append(
            {
                'name': ' '.join(item.find('a', class_='products-list-item__link link')
                                 .find('div', class_='products-list-item__brand').get_text().split()),
                'link': HOST + item.find('a').get('href'),
                'image': item.get('data-src'),
                'consist': characteristics['Состав:'] if 'Состав:' in characteristics else None,
                'season': characteristics['Сезон:'] if 'Сезон:' in characteristics else None,
                'color':  characteristics['Цвет:'] if 'Цвет:' in characteristics else None,
                'production_country': characteristics['Страна производства:'] if 'Страна производства:'
                                                                                 in characteristics else None
            }
        )
    return dresses


def to_csv(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['name', 'link',
                         'image', 'consist',
                         'season', 'color',
                         'production_country'])
        for item in items:
            writer.writerow([item['name'],
                             item['link'],
                             item['image'],
                             item['consist'],
                             item['season'],
                             item['color'],
                             item['production_country']])


def parser():
    dresses = []
    html = get_html(URL)
    if html.status_code == 200:
        for page in range(1, PAGES+1):
            print(page)
            time.sleep(60
                       )
            html = get_html(URL, params={'page': str(page)})
            dresses.extend(get_content(html.text))
            to_csv(dresses, CSV)
    else:
        print('Error')



parser()





