from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, select
from src.models.product_model import Product
from src.shared.database.session_db import SessionDep

app = FastAPI()

class CreateProduct(BaseModel):
    name: str
    price: float = Field(gt=10000)
    quantity: int = Field(gt=0)
    category: str


@app.post("/product", status_code=201)
def create_product(product_data: CreateProduct, session: SessionDep):

    existing_product = session.exec(
        select(Product).where(Product.name == product_data.name.strip().lower())
    ).first()

    if existing_product: raise HTTPException(status_code=409, detail="A product with that name already exists")

    product = Product(
        name=product_data.name.strip().lower(),
        category=product_data.category.strip().lower(),
        price=product_data.price,
        quantity=product_data.quantity,
    )

    session.add(product)
    session.commit()
    session.refresh(product)

    return {
        "message": "Product created successfully",
        "product": product
    }

@app.get("/product")
def get_products(session: SessionDep):
    products = session.exec(
        select(Product)
    ).all()
    if not products: raise HTTPException(status_code=404, detail="No products found")
    return products 

@app.delete('/product/{id}')
def delete_product(product_id: int, session: SessionDep):
    product = session.exec(
            select(Product).where(Product.id == product_id)
    ).one()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    raise HTTPException(status_code=204, detail="Product deleted successfully")