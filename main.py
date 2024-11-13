from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func,desc
from typing import List,Optional
from database import SessionLocal, engine, Base
from models import SalesProducts
from schemas import SalesProductBase, SalesProduct, SalesSummary
from faker import Faker
import random
from datetime import datetime

# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

fake = Faker()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Generate dummy data for initial setup
# @app.on_event("startup")
# def seed_data():
#     db = SessionLocal()
#     for _ in range(5):  # Create 5 dummy records
#         fake_product = SalesProducts(
#             product_name=fake.name(),
#             product_sku=fake.bothify(text="SKU-#####"),
#             total_sales_value=random.uniform(100, 1000),
#             orders_count=random.randint(1, 100)
#         )
#         db.add(fake_product)  
#     db.commit()
#     db.close()

# GET all products
@app.get("/sales-products/", response_model=list[SalesProduct])
def get_sales_products(db: Session = Depends(get_db)):
    products = db.query(SalesProducts).all()
    return products

# Create a new product
@app.post("/sales-products/", response_model=SalesProduct)
def create_sales_product(product: SalesProductBase, db: Session = Depends(get_db)):
    new_product = SalesProducts(
        product_name=product.product_name,
        product_sku=product.product_sku,
        total_sales_value=product.total_sales_value,
        orders_count=product.orders_count,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Update an existing product by ID
@app.put("/sales-products/{product_id}", response_model=SalesProduct)
def update_sales_product(product_id: int, product: SalesProductBase, db: Session = Depends(get_db)):
    db_product = db.query(SalesProducts).filter(SalesProducts.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.product_name = product.product_name
    db_product.product_sku = product.product_sku
    db_product.total_sales_value = product.total_sales_value
    db_product.orders_count = product.orders_count

    db.commit()
    db.refresh(db_product)
    return db_product

# Delete a product by ID
@app.delete("/sales-products/{product_id}", response_model=SalesProduct)
def delete_sales_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(SalesProducts).filter(SalesProducts.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return db_product

@app.get("/top-products/", response_model=List[SalesProduct])
def get_top_10_products(db: Session = Depends(get_db)):
    products = db.query(SalesProducts).order_by(desc(SalesProducts.total_sales_value)).limit(10).all()
    
    return products


@app.get("/products-duplicate-names/", response_model=List[SalesProduct])
def get_products_duplicate_names(db: Session = Depends(get_db)):
    subquery = (
        db.query(SalesProducts.product_name)
        .group_by(SalesProducts.product_name)
        .having(func.count(SalesProducts.product_name) > 1)
        .subquery()
    )
    
    products = db.query(SalesProducts).filter(SalesProducts.product_name.in_(subquery)).all()
    
    return products

@app.get("/products-by-date/", response_model=List[SalesProduct])
def get_products_by_date(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Helper function to parse dates
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if date_str:
            try:
                clean_date_str = date_str.strip().strip('"')
                return datetime.strptime(clean_date_str, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date format: '{date_str}'. Use YYYY-MM-DD."
                )
        return None

    # Parse start and end dates
    start_date_parsed = parse_date(start_date)
    end_date_parsed = parse_date(end_date)

    # Build the query using parsed dates
    query = db.query(SalesProducts)

    if start_date_parsed and end_date_parsed:
        query = query.filter(SalesProducts.created_at.between(start_date_parsed, end_date_parsed))
    elif start_date_parsed:
        query = query.filter(SalesProducts.created_at >= start_date_parsed)
    elif end_date_parsed:
        query = query.filter(SalesProducts.created_at <= end_date_parsed)


    # Execute the query and return the result
    products = query.all()
    return products


@app.get("/products-by-alphabet/", response_model=List[SalesProduct])
def get_products_by_alphabet(
    alphabet: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Validate the alphabet input
    if alphabet:
        if not alphabet.isalpha() or len(alphabet) != 1:
            raise HTTPException(
                status_code=400,
                detail="Invalid alphabet. Please provide a single alphabet character."
            )
        # Convert to uppercase to ensure case-insensitive search
        alphabet = alphabet.upper()

    # Build the query
    query = db.query(SalesProducts)

    # Apply filtering if alphabet is provided
    if alphabet:
        query = query.filter(func.upper(SalesProducts.product_name).like(f"{alphabet}%"))
    
    products = query.all()
    
    return products
