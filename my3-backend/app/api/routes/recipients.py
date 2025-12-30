from uuid import UUID
from typing import List
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import logging
from app.database.connection import get_db
from app.database.models import User, Recipient, Occasion, GiftIdea, RecipientRelationship
from app.database.schemas import (
    RecipientCreate, RecipientUpdate, RecipientResponse, 
    RecipientDetailResponse, OccasionResponse, GiftIdeaResponse
)
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recipients", tags=["recipients"])


@router.get("", response_model=List[RecipientResponse])
async def get_recipients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all recipients for current user.
    Returns recipients sorted by created_at descending.
    Includes count of upcoming occasions per recipient.
    """
    today = date.today()
    
    # Get recipients with occasion counts
    result = await db.execute(
        select(
            Recipient,
            func.count(Occasion.id).filter(
                and_(
                    Occasion.date >= today,
                    Occasion.status != "done"
                )
            ).label("upcoming_occasions_count")
        )
        .outerjoin(Occasion, Recipient.id == Occasion.recipient_id)
        .where(Recipient.user_id == current_user.id)
        .group_by(Recipient.id)
        .order_by(Recipient.created_at.desc())
    )
    
    recipients_with_counts = result.all()
    
    # Load relationships
    relationships_result = await db.execute(
        select(RecipientRelationship).where(RecipientRelationship.user_id == current_user.id)
    )
    relationships = relationships_result.scalars().all()
    
    # Build relationship map
    relationships_map = {}
    for rel in relationships:
        from_id = str(rel.from_recipient_id)
        if from_id not in relationships_map:
            relationships_map[from_id] = []
        relationships_map[from_id].append({
            "to_recipient_id": str(rel.to_recipient_id),
            "relationship_type": rel.relationship_type,
            "is_bidirectional": rel.is_bidirectional
        })
    
    # Format response
    recipients = []
    for recipient, occasion_count in recipients_with_counts:
        recipient_dict = {
            "id": recipient.id,
            "user_id": recipient.user_id,
            "name": recipient.name,
            "relationship": recipient.relationship_type,
            "age_band": recipient.age_band,
            "interests": recipient.interests or [],
            "constraints": recipient.constraints or [],
            "notes": recipient.notes,
            "is_core_contact": recipient.is_core_contact,
            "network_level": recipient.network_level,
            "street_address": recipient.street_address,
            "city": recipient.city,
            "state_province": recipient.state_province,
            "postal_code": recipient.postal_code,
            "country": recipient.country,
            "address_validation_status": recipient.address_validation_status,
            "created_at": recipient.created_at,
            "updated_at": recipient.updated_at,
            "upcoming_occasions_count": occasion_count or 0,
            "relationships": relationships_map.get(str(recipient.id), [])
        }
        recipients.append(RecipientResponse(**recipient_dict))
    
    logger.info(f"Retrieved {len(recipients)} recipients for user {current_user.id}")
    return recipients


@router.get("/{recipient_id}", response_model=RecipientDetailResponse)
async def get_recipient(
    recipient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific recipient with full details.
    Includes occasions and past gifts.
    """
    # Get recipient
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
    
    # Get occasions for this recipient
    occasions_result = await db.execute(
        select(Occasion).where(Occasion.recipient_id == recipient_id)
        .order_by(Occasion.date.desc() if Occasion.date else Occasion.created_at.desc())
    )
    occasions = occasions_result.scalars().all()
    
    # Get past gifts (gifts from occasions that are done or have passed)
    today = date.today()
    past_occasions_ids = [
        o.id for o in occasions 
        if (o.date and o.date < today) or o.status.value == "done"
    ]
    
    past_gifts = []
    if past_occasions_ids:
        gifts_result = await db.execute(
            select(GiftIdea).where(GiftIdea.occasion_id.in_(past_occasions_ids))
            .order_by(GiftIdea.created_at.desc())
        )
        past_gifts = gifts_result.scalars().all()
    
    # Count upcoming occasions
    upcoming_occasions_count = sum(
        1 for o in occasions 
        if o.date and o.date >= today and o.status.value != "done"
    )
    
    # Load relationships for this recipient
    relationships_result = await db.execute(
        select(RecipientRelationship).where(RecipientRelationship.user_id == current_user.id)
        .where(RecipientRelationship.from_recipient_id == recipient_id)
    )
    relationships = relationships_result.scalars().all()
    
    relationships_list = [
        {
            "to_recipient_id": str(rel.to_recipient_id),
            "relationship_type": rel.relationship_type,
            "is_bidirectional": rel.is_bidirectional
        }
        for rel in relationships
    ]
    
    # Format response
    recipient_dict = {
        "id": recipient.id,
        "user_id": recipient.user_id,
        "name": recipient.name,
        "relationship": recipient.relationship_type,
        "age_band": recipient.age_band,
        "interests": recipient.interests or [],
        "constraints": recipient.constraints or [],
        "notes": recipient.notes,
        "is_core_contact": recipient.is_core_contact,
        "network_level": recipient.network_level,
        "street_address": recipient.street_address,
        "city": recipient.city,
        "state_province": recipient.state_province,
        "postal_code": recipient.postal_code,
        "country": recipient.country,
        "address_validation_status": recipient.address_validation_status,
        "created_at": recipient.created_at,
        "updated_at": recipient.updated_at,
        "upcoming_occasions_count": upcoming_occasions_count,
        "relationships": relationships_list,
        "occasions": [OccasionResponse.model_validate(o) for o in occasions],
        "past_gifts": [GiftIdeaResponse.model_validate(g) for g in past_gifts]
    }
    
    logger.info(f"Retrieved recipient {recipient_id} with {len(occasions)} occasions and {len(past_gifts)} past gifts")
    return RecipientDetailResponse(**recipient_dict)


@router.post("", response_model=RecipientResponse, status_code=status.HTTP_201_CREATED)
async def create_recipient(
    recipient_data: RecipientCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new recipient."""
    # Create recipient
    new_recipient = Recipient(
        user_id=current_user.id,
        **recipient_data.model_dump()
    )
    
    # Validate address if provided
    if new_recipient.street_address and new_recipient.city:
        from app.services.address_validator import validate_address
        import json
        validation_result = await validate_address(
            street=new_recipient.street_address,
            city=new_recipient.city,
            state=new_recipient.state_province,
            postal_code=new_recipient.postal_code,
            country=new_recipient.country
        )
        new_recipient.address_validation_status = validation_result.get("status", "unvalidated")
        if validation_result.get("normalized_address"):
            new_recipient.validated_address_json = json.dumps(validation_result["normalized_address"])
    else:
        new_recipient.address_validation_status = "unvalidated"
    
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
    
    # Track if address changed
    address_changed = False
    old_street = recipient.street_address
    old_city = recipient.city
    
    # Update fields
    update_data = recipient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recipient, field, value)
        # Check if address fields changed
        if field in ["street_address", "city", "state_province", "postal_code", "country"]:
            address_changed = True
    
    # Validate address if changed and complete
    if address_changed and recipient.street_address and recipient.city:
        from app.services.address_validator import validate_address
        import json
        validation_result = await validate_address(
            street=recipient.street_address,
            city=recipient.city,
            state=recipient.state_province,
            postal_code=recipient.postal_code,
            country=recipient.country
        )
        recipient.address_validation_status = validation_result.get("status", "unvalidated")
        if validation_result.get("normalized_address"):
            recipient.validated_address_json = json.dumps(validation_result["normalized_address"])
        else:
            recipient.validated_address_json = None
    
    await db.commit()
    await db.refresh(recipient)
    
    return recipient


@router.delete("/{recipient_id}")
async def delete_recipient(
    recipient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a recipient.
    Cascades delete to occasions (and their gift ideas).
    Returns success message.
    """
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
    
    recipient_name = recipient.name
    
    # Delete recipient (cascade will handle occasions and gift ideas)
    # In SQLAlchemy 2.0 async, use delete() method
    await db.delete(recipient)
    await db.commit()
    
    logger.info(f"Deleted recipient {recipient_id} ({recipient_name}) for user {current_user.id}")
    
    return {
        "message": f"Recipient '{recipient_name}' and all associated occasions have been deleted successfully."
    }

