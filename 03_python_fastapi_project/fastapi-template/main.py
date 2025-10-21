from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import Product, create_tables, get_db
from fastapi.middleware.cors import CORSMiddleware
from cart import router as cart_router


class ProductCreate(BaseModel):
  name: str
  price: float
  description: str | None = None
  stock: int
  
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    stock: Optional[int] = None


class ProductResponse(BaseModel):
  id: int
  name: str
  price: float
  description: str | None = None
  stock: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Template"}


@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.name == product.name))
    db_product = result.first()

    if db_product:
        raise HTTPException(status_code=400, detail="Product already registered")

    db_product = Product(
        name=product.name,
        price=product.price,
        description=product.description,
        stock=product.stock,
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductUpdate, db: AsyncSession = Depends(get_db)):
    db_product = await db.get(Product, product_id)

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found with this id")

    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    await db.commit()
    await db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", status_code=204)
async def get_products(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product = await db.get(Product, product_id)

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(db_product)
    await db.commit()

    return

@app.get("/products/", response_model=List[ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(cart_router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
