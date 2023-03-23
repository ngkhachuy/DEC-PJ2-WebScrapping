from sqlalchemy import Column, String, Text, BIGINT, Integer, Float, DOUBLE, DATETIME
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PRODUCTS(Base):
    __tablename__ = 'products'

    ID = Column(String(255), primary_key=True)
    TITLE = Column(Text)
    BRAND = Column(String(255))
    RATING = Column(Float)
    COUNT_OF_RATE = Column(Integer)
    CURRENT_PRICE = Column(Float)
    SHIPPING_PRICE = Column(Float)
    TOTAL_PRICE = Column(Float)
    IMG_URL = Column(Text)
    ITEM_URL = Column(Text)
    MAX_RESOLUTION = Column(String(255))
    DISPLAY_PORT = Column(String(255))
    HDMI = Column(String(255))
    DIRECT_X = Column(String(255))
    MODEL = Column(String(255))
    CREATED_TIME = Column(DATETIME)

    def __repr__(self):
        return "<TITLE: {0} - CURRENT_PRICE: {1}>".format(self.TITLE, self.CURRENT_PRICE)
