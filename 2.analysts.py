import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


if __name__ == '__main__':

    data = pd.read_csv('data/items_2023-03-21 21:43:49.805758.csv')

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
    fig, ax = plt.subplots(2, 2, figsize=(18, 7))

    # 01. Brand name and number of products.
    brand_count = data.groupby(['BRAND']).size().reset_index(name='count')
    brand_count.sort_values('count', inplace=True)
    print(brand_count.tail(10))

    gs = ax[0, 1].get_gridspec()
    ax[0, 0].remove()
    ax[0, 1].remove()
    axbig = fig.add_subplot(gs[0, :])
    sns.barplot(y='BRAND', x='count', data=brand_count.tail(10), ax=axbig)
    axbig.set_title('Top10 Featured Brands')
    axbig.set(ylabel=None, xlabel='Number of Product')

    # 02. Distribution of price
    current_price = data[(data['CURRENT_PRICE'] > 0)]
    current_price_under4000 = current_price[(current_price['CURRENT_PRICE'] <= 3000)]
    current_price_over4000 = current_price[(current_price['CURRENT_PRICE'] > 3000)]
    print(current_price['CURRENT_PRICE'].describe())

    sns.histplot(current_price_under4000, x='CURRENT_PRICE', ax=ax[1, 0])
    ax[1, 0].set_title('Distribution of price (under $3000')
    sns.histplot(current_price_over4000, x='CURRENT_PRICE', ax=ax[1, 1])
    ax[1, 1].set_title('Distribution of price (over $3000')

    plt.show()
