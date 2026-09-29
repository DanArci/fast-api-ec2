import os
import uuid
from io import BytesIO

import boto3
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Field, select

from src.models.product_model import Product
from src.shared.database.session_db import SessionDep

app = FastAPI(title="FastAPI EC2 API")

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class CreateProduct(BaseModel):
    name: str
    price: float = Field(gt=10000)
    quantity: int = Field(gt=0)
    category: str


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Application is running"}


@app.post("/images")
async def upload_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required")

    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .jpg, .jpeg, .png, and .webp images are allowed",
        )

    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="The uploaded file must be an image")

    bucket_name = os.getenv("AWS_S3_BUCKET")
    if not bucket_name:
        raise HTTPException(status_code=500, detail="AWS_S3_BUCKET is not configured")

    region_name = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")
    session_kwargs = {}
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")

    if access_key:
        session_kwargs["aws_access_key_id"] = access_key
    if secret_key:
        session_kwargs["aws_secret_access_key"] = secret_key
    if session_token:
        session_kwargs["aws_session_token"] = session_token
    if region_name:
        session_kwargs["region_name"] = region_name

    try:
        s3_client = boto3.Session(**session_kwargs).client("s3")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error creating AWS S3 client: {exc}") from exc

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded image is empty")

    s3_key = f"images/{uuid.uuid4()}-{file.filename}"

    try:
        s3_client.upload_fileobj(BytesIO(file_bytes), bucket_name, s3_key)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to upload image to S3: {exc}") from exc

    if region_name:
        image_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_key}"
    else:
        image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

    return {
        "message": "Image uploaded successfully",
        "bucket": bucket_name,
        "key": s3_key,
        "url": image_url,
    }


@app.post("/product", status_code=201)
def create_product(product_data: CreateProduct, session: SessionDep):
    existing_product = session.exec(
        select(Product).where(Product.name == product_data.name.strip().lower())
    ).first()

    if existing_product:
        raise HTTPException(status_code=409, detail="A product with that name already exists")

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
        "product": product,
    }


@app.get("/product")
def get_products(session: SessionDep):
    products = session.exec(select(Product)).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    return products


@app.delete("/product/{product_id}")
def delete_product(product_id: int, session: SessionDep):
    product = session.exec(select(Product).where(Product.id == product_id)).one()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    raise HTTPException(status_code=204, detail="Product deleted successfully")