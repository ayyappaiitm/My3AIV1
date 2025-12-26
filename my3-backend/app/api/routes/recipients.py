from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.connection import get_db
from app.database.models import User, Recipient
from app.database.schemas import RecipientCreate, RecipientUpdate, RecipientResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/recipients", tags=["recipients"])

MAX_RECIPIENTS = 10


@router.get("", response_model=List[RecipientResponse])
async def get_recipients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all recipients for current user."""
    result = await db.execute(
        select(Recipient).where(Recipient.user_id == current_user.id)
    )
    recipients = result.scalars().all()
    return recipients


@router.get("/{recipient_id}", response_model=RecipientResponse)
async def get_recipient(
    recipient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific recipient."""
    result = await db.execute(
        select(Recipient).where(
            Recipient.id == recipient_id,
            Recipient.user_id == current_user.id
        )
    )
    recipient = result.scalar_one_or_none()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    return recipient


@router.post("", response_model=RecipientResponse, status_code=status.HTTP_201_CREATED)
async def create_recipient(
    recipient_data: RecipientCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new recipient. Enforces max 10 recipients per user."""
    # Check recipient count
    count_result = await db.execute(
        select(func.count(Recipient.id)).where(Recipient.user_id == current_user.id)
    )
    count = count_result.scalar()
    
    if count >= MAX_RECIPIENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_RECIPIENTS} recipients allowed per user"
        )
    
    # Create recipient
    new_recipient = Recipient(
        user_id=current_user.id,
        **recipient_data.model_dump()
    )
    
    db.add(new_recipient)
    await db.commit()
    await db.refresh(new_recipient)
    
    return new_recipient


@router.put("/{recipient_id}", response_model=RecipientResponse)
async def update_recipient(
    recipient_id: UUID,
    recipient_data: RecipientUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a recipient."""
    result = await db.execute(
        select(Recipient).where(
            Recipient.id == recipient_id,
            Recipient.user_id == current_user.id
        )
    )
    recipient = result.scalar_one_or_none()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    # Update fields
    update_data = recipient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recipient, field, value)
    
    await db.commit()
    await db.refresh(recipient)
    
    return recipient


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipient(
    recipient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a recipient."""
    result = await db.execute(
        select(Recipient).where(
            Recipient.id == recipient_id,
            Recipient.user_id == current_user.id
        )
    )
    recipient = result.scalar_one_or_none()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    await db.delete(recipient)
    await db.commit()
    
    return None

