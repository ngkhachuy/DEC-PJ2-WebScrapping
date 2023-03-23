import pandas as pd
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from PRODUCT import Base


def clean_string(ip_str):
    ip_str.strip().replace('\n', ' ')
    ip_str.replace('\r', '')
    return ip_str


def read_data_from_db():
    engine = db.create_engine('mysql+mysqlconnector://root:123456@localhost:3306/graphics_cards')
    conn = engine.connect()
    rtn = pd.read_sql(db.text('SELECT * FROM products;'), conn)
    conn.close()
    return rtn


def execute_sql(sql):
    engine = db.create_engine('mysql+mysqlconnector://root:123456@localhost:3306/graphics_cards')
    conn = engine.connect()
    rtn = pd.read_sql(db.text(sql), conn)
    conn.close()
    return rtn


def import_into_database(data):

    engine = db.create_engine('mysql+mysqlconnector://root:123456@localhost:3306/graphics_cards')

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session = sessionmaker()
    session.configure(bind=engine)
    my_session = session()

    data.to_sql('products', engine, if_exists='replace', index=False)

    my_session.commit()
    my_session.close()
