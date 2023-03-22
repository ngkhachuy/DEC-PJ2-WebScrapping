from datetime import datetime, timedelta
import time
import re

import requests
import pandas as pd
from bs4 import BeautifulSoup

if __name__ == '__main__':

    START = datetime.now()
    num_of_page = 100

    url = 'https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-%d?Tid=7709'
    list_product = []
    num_of_req = 0

    for i in range(num_of_page):

        PAGE = url % (i + 1)
        print('Send request to Page %d!' % (i + 1))

        err = True
        while err:
            res = requests.get(PAGE).text
            num_of_req += 1
            context = BeautifulSoup(res, 'html.parser')
            cells = context.find_all('div', class_='item-cell')
            # item_blocks = context.find_all('div', class_='item-container')
            if 'Are you a human?' in context.text:
                print("Host blocked! Wait for 60m. (Req count: %d)" % num_of_req)
                print("Continue at: ", datetime.now() + timedelta(minutes=60))
                num_of_req = 0
                time.sleep(3600)
            else:
                err = False

        item_index = 0
        for item in cells:

            item_index += 1
            item_detail = item.find('a', class_='item-title')
            item_url = item_detail['href']
            # print("Get details item: ", item_index)

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

            # LOAD EACH PRODUCT FOR MORE DETAILS
            err = True
            while err:
                item_res = requests.get(item_url).text
                item_context = BeautifulSoup(item_res, 'html.parser')
                num_of_req += 1
                if 'Are you a human?' in context.text:
                    print("Host blocked! Wait for 60m. (Req count: %d)" % num_of_req)
                    print("Continue at: ", datetime.now() + timedelta(minutes=60))
                    num_of_req = 0
                    time.sleep(3600)
                else:
                    err = False

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
                'MODEL': model
            }
            list_product.append(product)

    print(num_of_req)
    df = pd.DataFrame(list_product)
    df.to_csv("data/items_%s.csv" % START, index=False)
    # print(df)
    print("TOTAL ITEMS: ", len(df), "items")
    print("EXECUTING TIME: ", datetime.now() - START)
