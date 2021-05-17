import logging
import requests
from bs4 import BeautifulSoup
import csv
from time import sleep
from random import uniform

CSV = 'dresses.csv'
PAGES = 50
HOST = 'https://www.6pm.com'
URL = 'https://www.6pm.com/dresses/CKvXARDE1wHiAgIBAg.zso'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.1.112 Yowser/2.5 Safari/537.36'
}


def get_html(url, user_agent=None, proxy=None, params=None):
    response = requests.get(url, headers=HEADERS, proxies=proxy, params=params)
    #print(response.status_code)
    return response


def get_characteristics(url, params=''):
    consist = ''
    characteristic = {}
    request = requests.get(url, headers=HEADERS, params=params)
    soup = BeautifulSoup(get_html(url).text, 'html.parser')
    all_characteristics = soup.find('div', class_='WK')
    descr = all_characteristics.find('ul').find_all('li')
    for i in descr:
        if '%' in i.text:
            consist += " " + i.text.replace('.', '')
            if ';' in consist:
                consist.replace(';', ' ')
        else:
            pass
    characteristic['color'] = soup.find(itemprop='color').get('content')
    characteristic['consist'] = consist
    characteristic['description'] = all_characteristics.find('li', class_='VK').get_text()
    return characteristic


def get_content(html):
    dresses = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(class_='vh Sh Fh Ih')
    n = 0
    for item in items:
        print(f'Парсится товар номер {n+1}')
        url_of_item = HOST + item.find('a', itemprop='url').get('href')
        sleep(uniform(3, 10))
        characteristics = get_characteristics(url_of_item)
        dresses.append(
            {
                'brand': item.find('p', class_='Th', itemprop='brand').get_text(),
                'name': item.find('p', class_='Uh', itemprop='name').get_text(),
                'link': url_of_item,
                'image': item.find('meta', itemprop='image').get('content'),
                'color': characteristics['color'],
                'consist': characteristics['consist'],
                'description': characteristics['description']
            }

        )
        print(dresses[n])
        n += 1
    return dresses


def to_csv(items, path):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['brand', 'name', 'link',
                         'image', 'color',
                         'consist', 'description'])
        for item in items:
            writer.writerow([item['brand'],
                             item['name'],
                             item['link'],
                             item['image'],
                             item['color'],
                             item['consist'],
                             item['description']])


def parser():
    dresses = []
    html = get_html(URL)
    if html.status_code == 200:
        for page in range(1, PAGES+1):
            print(f'Парсится страница номер {page}')
            html = get_html(URL, params={'page': str(page)})
            dresses.extend(get_content(html.text))
            to_csv(dresses, CSV)
    else:
        print('Error')


def main():
    parser()


if __name__ == '__main__':
    main()







