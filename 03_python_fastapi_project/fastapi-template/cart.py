from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import CartItem, Product, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: dict

router = APIRouter()

@router.get("/cart/", response_model=list[CartItemResponse])
async def get_cart(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CartItem).options(selectinload(CartItem.product))
    )
    items = result.scalars().all()
    return [
        CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            product={
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                "description": item.product.description,
                "stock": item.product.stock,
            },
        )
        for item in items
    ]

@router.post("/cart/", response_model=CartItemResponse)
async def add_to_cart(cart_item: CartItemCreate, db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            product = await db.get(Product, cart_item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            if product.stock < cart_item.quantity:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough stock")
            result = await db.execute(
                select(CartItem).where(CartItem.product_id == cart_item.product_id)
            )
            item = result.scalar_one_or_none()
            if item:
                item.quantity += cart_item.quantity
            else:
                item = CartItem(product_id=cart_item.product_id, quantity=cart_item.quantity)
                db.add(item)
            product.stock -= cart_item.quantity
        # Transaction is committed by context manager; refresh entities
        await db.refresh(item)
        await db.refresh(product)
        return CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            product={
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "stock": product.stock
            }
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/cart/{item_id}", status_code=204)
async def remove_from_cart(item_id: int, db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            item = await db.get(CartItem, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Cart item not found")
            product = await db.get(Product, item.product_id)
            if product:
                product.stock += item.quantity
            await db.delete(item)
        await db.commit()
        return
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
