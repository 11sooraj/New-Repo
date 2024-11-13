from pydantic import BaseModel
from datetime import datetime

# Base model for sales product
class SalesProductBase(BaseModel):
    product_name: str
    product_sku: str
    total_sales_value: float
    orders_count: int

# Extended model with additional fields
class SalesProduct(SalesProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SalesSummary(BaseModel):
    created_date: datetime  
    total_sales: int
    Total_Sales: float
