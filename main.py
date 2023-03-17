import datetime
import re

import requests
import pandas as pd
from bs4 import BeautifulSoup


if __name__ == '__main__':

    START = datetime.datetime.now()
    num_of_page = 1

    url = 'https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-%d?Tid=7709'
    list_product = []

    for i in range(num_of_page):
        PAGE = url % (i + 1)
        # PAGE = 'https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-4?Tid=7709'
        print('Send request to Page %d!' % (i + 1))
        res = requests.get(PAGE, params={'check': True}).text
        context = BeautifulSoup(res, 'html.parser')
        print(context.prettify())

        item_blocks = context.find_all('div', class_='item-container')

        for item in item_blocks:

            item_detail = item.find('a', class_='item-title')
            item_url = item_detail['href']
            print("Get details item: : ", item_url)

            # ITEM INFOR
            item_id = item_url.split('/')[-1]
            item_title = item_detail.text
            item_brand = item.find('a', class_='item-brand')
            if item_brand is not None:
                item_brand = item_brand.find('img')['alt']

            # RATING AND COUNT OF RATE
            rating = 0
            count_of_rate = 0
            try:
                rating = item.find('a', class_='item-rating')['title'].replace('Rating + ', '')
                count_of_rate = item.find('span', class_='item-rating-num').text.strip('()')
            except AttributeError:
                pass
            except TypeError:
                pass

            # CURRENT PRICE
            curent_price = item.find('li', class_='price-current').text
            curent_price = re.findall('\\d+.\\d+', curent_price)[0]
            curent_price = curent_price.replace(',', '')

            # SHIPPING PRICE
            shipping_price = item.find('li', class_='price-ship').text
            if shipping_price == 'Free Shipping':
                shipping_price = 0
            else:
                shipping_price = re.findall('\\d+.\\d+', shipping_price)[0]

            # IMAGE's URL
            img_url = item.find('a', class_='item-img').find('img')['src']

            # LOAD EACH PRODUCT FOR MORE DETAILS
            item_res = requests.get(item_url).text
            item_context = BeautifulSoup(item_res, 'html.parser')

            # MAX RESOLUTION
            max_resolution = item_context.body.findAll(string='Max Resolution')
            if len(max_resolution) == 0:
                max_resolution = None
            else:
                max_resolution = max_resolution[0].parent.nextSibling.text

            # DISPLAY PORT
            display_port = item_context.body.findAll(string='DisplayPort')
            if len(display_port) == 0:
                display_port = None
            else:
                display_port = display_port[0].parent.nextSibling.text

            # HDMI
            hdmi = item_context.body.findAll(string='HDMI')
            if len(hdmi) == 0:
                hdmi = None
            else:
                hdmi = hdmi[0].parent.nextSibling.text

            # DIRECT X
            direct_x = item_context.body.findAll(string='DirectX')
            if len(direct_x) == 0:
                direct_x = None
            else:
                direct_x = direct_x[0].parent.nextSibling.text

            # MODEL
            model = item_context.body.findAll(string='Model')
            if len(model) == 0:
                model = None
            else:
                model = model[0].parent.nextSibling.text

            product = {
                'ID': item_id,
                'TITLE': item_title,
                'BRAND': item_brand,
                'RATING': rating,
                'COUNT_OF_RATE': count_of_rate,
                'CURRENT_PRICE': curent_price,
                'SHIPPING_PRICE': shipping_price,
                'IMG_URL': img_url,
                'MAX_RESOLUTION': max_resolution,
                'DISPLAY_PORT': display_port,
                'HDMI': hdmi,
                'DIRECT_X': direct_x,
                'MODEL': model,
                'TOTAL_PRICE': float(curent_price) + float(shipping_price)
            }
            list_product.append(product)

    df = pd.DataFrame(list_product)
    df.to_csv("items.csv", index=False)
    print(df)
    print("TOTAL ITEMS: ", len(df), "items")
    print("EXECUTING TIME: ", datetime.datetime.now() - START)
