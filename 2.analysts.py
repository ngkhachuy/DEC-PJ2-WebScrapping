import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import COMMON

if __name__ == '__main__':

    # Get Data from DB
    data = COMMON.read_data_from_db()
    data = data.astype({'RATING': float, 'COUNT_OF_RATE': int, 'CURRENT_PRICE': float, 'SHIPPING_PRICE': float})

    # Cleanning 'BRAND' column
    brand_list = list(data.BRAND)
    new_brand = []
    for k, item in data.iterrows():
        if pd.isna(item['BRAND']):
            new_item_brand = item['TITLE'].split(" ")[0]
            if new_item_brand in brand_list:
                new_brand.append(new_item_brand)
            else:
                new_brand.append(None)
        else:
            new_brand.append(item['BRAND'])
    data['BRAND'] = new_brand
    data.dropna(subset=['BRAND'], inplace=True)

    # Create visualization
    fig, ax = plt.subplots(3, 3, figsize=(15, 30))

    # 01. Brand name and number of products.
    brand_count = data.groupby(['BRAND']).size().reset_index(name='count')
    brand_count.sort_values('count', inplace=True)
    print(brand_count.tail(10))

    gs = ax[0, 1].get_gridspec()
    ax[0, 0].remove()
    ax[0, 1].remove()
    axbig1 = fig.add_subplot(gs[0, :-1])
    sns.barplot(y='BRAND', x='count', data=brand_count.tail(10), ax=axbig1)
    axbig1.set_title('Top10 Featured Brands')
    axbig1.set(ylabel=None)

    # 02. Distribution of Price
    break_point = 2000
    current_price = data[(data['CURRENT_PRICE'] > 0)]
    current_price_under4000 = current_price[(current_price['CURRENT_PRICE'] <= break_point)]
    current_price_over4000 = current_price[(current_price['CURRENT_PRICE'] > break_point)]
    print(current_price['CURRENT_PRICE'].describe())

    sns.histplot(current_price_under4000, x='CURRENT_PRICE', ax=ax[1, 0])
    ax[1, 0].set_title('Distribution of price (under $%d)' % break_point)
    sns.histplot(current_price_over4000, x='CURRENT_PRICE', ax=ax[1, 1])
    ax[1, 1].set_title('Distribution of price (higher $%d)' % break_point)

    # 3. Distribution of Price by Brand
    gs = ax[0, 1].get_gridspec()
    ax[0, 2].remove()
    ax[1, 2].remove()
    ax[2, 2].remove()
    axbig2 = fig.add_subplot(gs[0:, -1])
    price_by_brand = data.loc[:, ['BRAND', 'CURRENT_PRICE']]
    sns.scatterplot(price_by_brand, x='CURRENT_PRICE', y='BRAND', ax=axbig2)
    axbig2.set_title('Distribution of Price by Brand')
    axbig2.set(ylabel=None)

    # 4. Correlation of Rating and Price
    rating_vs_price = data.loc[(data['RATING'] > 0) & (data['CURRENT_PRICE'] > 0), ['RATING', 'CURRENT_PRICE']]
    print(rating_vs_price)

    gs = ax[2, 1].get_gridspec()
    ax[2, 0].remove()
    ax[2, 1].remove()
    axbig3 = fig.add_subplot(gs[2, :-1])
    sns.scatterplot(rating_vs_price, x='CURRENT_PRICE', y='RATING', ax=axbig3)
    axbig3.set_title('Correlation of Rating and Price')

    plt.subplots_adjust(hspace=0.3)
    plt.show()
