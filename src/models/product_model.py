from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    __tablename__ = "app_inv_products"

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(unique=True)
    price: float = Field(gt=10000)
    category: str
    quantity: int = Field(gt=0)

