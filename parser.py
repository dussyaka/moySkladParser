import requests
import csv
from dataclasses import dataclass
from dotenv import load_dotenv
from os import environ
import shutil


MAIN_URL = "https://api.moysklad.ru/api/remap/1.2"


@dataclass
class Product:
    id: str
    name: str
    article: str
    price: float
    supplier: str | None = None


class MoySkladAPI():

    access_token: str | None = None
    session: requests.Session | None = None


    def __init__(self, access_token: str):

        self.session = requests.session()
        self.access_token = access_token
        self.session.headers['Authorization'] = 'Bearer ' + access_token
        self.session.headers['Accept-Encoding'] = 'gzip'


    def get_stock(self):

        url = MAIN_URL + '/report/stock/all/current'

        response = self.session.get(url)

        if not response.ok:
            print('Произошла ошибка при получении остатков.')
            print(response.status_code, response.content.decode())
            return

        response_data = response.json()

        stock = {}

        for d in response_data:
            stock[d['assortmentId']] = d['stock']

        return stock


    def _get_products(self, offset: int = 0):

        url = MAIN_URL + '/entity/product'
        params = {
            'offset': offset
        }

        response = self.session.get(url, params=params)

        if not response.ok:
            print('Произошла ошибка при получении товаров.')
            print(response.status_code, response.content.decode())
            return

        return response.json()


    def get_products(self) -> list[Product]:

        products = []
        offset = 0

        while True:

            data = self._get_products(offset)

            if data['meta']['limit'] + data['meta']['offset'] > data['meta']['size']:
                has_next = False
            else:
                has_next = True

            for row in data['rows']:

                # Определяем цену
                price = 1
                for sp in row['salePrices']:
                    if sp['priceType']['name'] == 'Цена продажи':
                        price = sp['value'] / 100
                        break

                # Определяем производителя
                supplier = None
                for attr in row['attributes']:
                    if attr['name'] == 'Производитель':
                        supplier = attr['value']['name']

                article = row.get('article')
                if not article:
                    continue
                
                product = Product(
                    row['id'],
                    row['name'],
                    article,
                    price,
                    supplier
                )

                products.append(product)

            offset += 1000

            if not has_next:
                break

        return products


def main():

    load_dotenv()
    access_token = environ.get('ACCESS_TOKEN')
    path = environ.get('FILEPATH')

    api = MoySkladAPI(access_token)
    products = api.get_products()
    stock = api.get_stock()

    with open('output.csv', 'w', encoding='utf-8') as file:

        writer = csv.writer(file)
        writer.writerow(('ID', 'Артикул', 'Производитель', 'Наименование', 'Цена', 'Количество'))

        for product in products:

            count = stock.get(product.id)
            if not count or count < 1:
                continue

            writer.writerow((
                product.id,
                product.article,
                product.supplier,
                product.name,
                int(product.price),
                count
            ))

    shutil.move('output.csv', path)

if __name__ == '__main__':
    main()