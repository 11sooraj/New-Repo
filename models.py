from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class SalesProducts(Base):
    __tablename__ = 'sales_products'
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    product_sku = Column(String)
    total_sales_value = Column(Float)
    orders_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
