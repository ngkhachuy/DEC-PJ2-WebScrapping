from datetime import datetime, timedelta
import time

import requests
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup

from PRODUCT import PRODUCTS

if __name__ == '__main__':

    # MAX_RESOLUTION
    # 1441
    # DISPLAY_PORT
    # 1308
    # HDMI
    # 1610
    # DIRECT_X
    # 2729

    START = datetime.now()
    print("Started at %s" % START)

    count_updated_record = 0
    count_request = 0

    engine = db.create_engine('mysql+mysqlconnector://root:123456@localhost:3306/graphics_cards')
    session = sessionmaker()
    session.configure(bind=engine)
    my_session = session()

    data = my_session.query(PRODUCTS).all()

    for item in data:

        new_MAX_RESOLUTION = None
        new_DISPLAY_PORT = None
        new_HDMI = None
        new_DIRECT_X = None
        new_MODEL = None

        if item.MAX_RESOLUTION is None or item.DISPLAY_PORT is None \
                or item.HDMI is None or item.DIRECT_X is None or item.MODEL is None:

            err = True
            while err:
                res = requests.get(item.ITEM_URL)
                context = BeautifulSoup(res.text, 'html.parser')
                count_request += 1

                if res.status_code == 403 or 'Are you a human?' in context:
                    print("Host blocked! Sleep until %s" % (datetime.now() + timedelta(hours=1)))
                    print("Request send: %d" % count_request)
                    count_request = 0
                    time.sleep(3600)
                else:
                    err = False

            max_res = context.findAll('th')
            fetures = {}
            for t in max_res:
                fetures[t.text.strip()] = t.next_sibling.text

            # MAX_RESOLUTION
            if item.MAX_RESOLUTION is None:
                new_MAX_RESOLUTION = fetures.get('Max Resolution')
            else:
                new_MAX_RESOLUTION = item.MAX_RESOLUTION

            # DISPLAY_PORT
            if item.DISPLAY_PORT is None:
                new_DISPLAY_PORT = fetures.get('DisplayPort')
            else:
                new_DISPLAY_PORT = item.DISPLAY_PORT

            # HDMI
            if item.HDMI is None:
                new_HDMI = fetures.get('HDMI')
            else:
                new_HDMI = item.HDMI

            # DIRECT_X
            if item.DIRECT_X is None:
                new_DIRECT_X = fetures.get('DirectX')
            else:
                new_DIRECT_X = item.DIRECT_X

            # MODEL
            if item.MODEL is None:
                new_MODEL = fetures.get('Model')
            else:
                new_MODEL = item.MODEL

            # stmt = db.update(PRODUCTS).where(PRODUCTS.ID == item.ID).values({'MAX_RESOLUTION': new_MAX_RESOLUTION,
            #                                                                  'DISPLAY_PORT': new_DISPLAY_PORT,
            #                                                                  'HDMI': new_HDMI,
            #                                                                  'DIRECT_X': new_DIRECT_X,
            #                                                                  'MODEL': new_MODEL})
            stmt = db.text('UPDATE products '
                           'SET '
                           '    MAX_RESOLUTION = "%s", '
                           '    DISPLAY_PORT = "%s", '
                           '    HDMI = "%s", '
                           '    DIRECT_X = "%s", '
                           '    MODEL = "%s"'
                           'WHERE ID = "%s"'
                           % (new_MAX_RESOLUTION, new_DISPLAY_PORT, new_HDMI, new_DIRECT_X, new_MODEL, item.ID))
            rtn = my_session.execute(stmt)
            count_updated_record += rtn.rowcount

        else:
            continue

    my_session.commit()
    my_session.close()
    print("Update %d records." % count_updated_record)
    print("EXECUTING TIME: ", datetime.now() - START)
