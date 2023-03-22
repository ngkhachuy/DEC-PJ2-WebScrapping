from datetime import datetime
import re

import requests
import pandas as pd
from bs4 import BeautifulSoup

import COMMON

if __name__ == '__main__':

    START = datetime.now()
    num_of_page = 100

    url = 'https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-%d?Tid=7709'
    list_product = []

    for i in range(num_of_page):

        PAGE = url % (i + 1)
        # PAGE = 'https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-4?Tid=7709'
        print('Send request to Page %d!' % (i + 1))
        res = requests.get(PAGE).text
        context = BeautifulSoup(res, 'html.parser')
        cells = context.find_all('div', class_='item-cell')

        item_index = 0
        for item in cells:

            item_index += 1
            item_detail = item.find('a', class_='item-title')
            item_url = item_detail['href']

            if item['id'].split("_")[0] == 'item':
                type_item = 'SINGLE'

                # ITEM ID
                item_id = item_url.split('/')[-1]
                # ITEM BRAND
                item_brand = item.find('a', class_='item-brand')
                if item_brand is not None:
                    item_brand = item_brand.find('img')['alt']

                # RATING AND COUNT OF RATE
                try:
                    rating = item.find('a', class_='item-rating')['title'].replace('Rating + ', '')
                    count_of_rate = item.find('span', class_='item-rating-num').text.strip('()')
                except AttributeError:
                    rating = 0
                    count_of_rate = 0
                except TypeError:
                    rating = 0
                    count_of_rate = 0

            else:
                type_item = 'COMBO'

                # ITEM ID
                item_id = item_url.split('=')[-1]
                # ITEM BRAND
                item_brand = None
                # RATING AND COUNT OF RATE
                rating = 0
                count_of_rate = 0

            # ITEM TITLE
            item_title = item_detail.text.strip().replace('\n', ' ').replace('\r', '')

            # CURRENT PRICE
            try:
                curent_price = item.find('li', class_='price-current').text
                curent_price = re.findall('(\\d+.\\d+)', curent_price)[0]
                curent_price = curent_price.replace(',', '')
            except IndexError:
                curent_price = 0.0

            # SHIPPING PRICE
            shipping_price = item.find('li', class_='price-ship').text
            if shipping_price in ('Free Shipping', 'Special Shipping', '') or shipping_price is None:
                shipping_price = 0.0
            else:
                shipping_price = re.findall('\\d+.\\d+', shipping_price)[0]

            # IMAGE's URL
            img_url = item.find('a', class_='item-img').find('img')['src']

            # Get Item features
            item_features = item.find('ul', class_='item-features').children
            max_resolution = None
            display_port = None
            hdmi = None
            direct_x = None
            model = None
            for feat in item_features:
                feat_contents = feat.contents
                if feat_contents[0].text == 'Max Resolution:':
                    max_resolution = feat_contents[1].strip().replace('\n', ' ').replace('\r', '')
                elif feat_contents[0].text == 'DisplayPort:':
                    display_port = feat_contents[1].strip().replace('\n', ' ').replace('\r', '')
                elif feat_contents[0].text == 'HDMI:':
                    hdmi = feat_contents[1].strip().replace('\n', ' ').replace('\r', '')
                elif feat_contents[0].text == 'DirectX:':
                    direct_x = feat_contents[1].strip().replace('\n', ' ').replace('\r', '')
                elif feat_contents[0].text == 'Model #: ':
                    model = feat_contents[1].strip().replace('\n', ' ').replace('\r', '')

            product = {
                'PAGE': i + 1,
                'ID': item_id,
                # 'TYPE': type_item,
                'TITLE': item_title,
                'BRAND': item_brand,
                'RATING': rating,
                'COUNT_OF_RATE': count_of_rate,
                'CURRENT_PRICE': curent_price,
                'SHIPPING_PRICE': shipping_price,
                'TOTAL_PRICE': float(curent_price) + float(shipping_price),
                'IMG_URL': img_url,
                'ITEM_URL': item_url,
                'MAX_RESOLUTION': max_resolution,
                'DISPLAY_PORT': display_port,
                'HDMI': hdmi,
                'DIRECT_X': direct_x,
                'MODEL': model,
                'CREATED_TIME': START
            }
            list_product.append(product)

        print("Scraped %d products in page." % len(cells))

    data = pd.DataFrame(list_product)
    data.to_csv("data/items_%s.csv" % START, index=False)

    # Store data in DB
    COMMON.import_into_database(data)

    data_feature = data.loc[:, ['ID', 'MAX_RESOLUTION', 'DISPLAY_PORT', 'HDMI', 'MODEL']]
    data_feature.to_json("data/items_feature_%s.json" % START, orient="records")

    print("TOTAL ITEMS: ", len(data), "items")
    print("EXECUTING TIME: ", datetime.now() - START)
