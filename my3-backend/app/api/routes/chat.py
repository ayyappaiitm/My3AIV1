from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from langchain_core.messages import HumanMessage
import logging
from app.database.connection import get_db
from app.database.models import User, Conversation, Message, Recipient, Occasion, OccasionStatus, RecipientRelationship
from app.database.schemas import ChatRequest, ChatResponse, ChatConfirmRequest, ChatConfirmResponse
from app.api.dependencies import get_current_user
from app.graph.workflow import my3_graph
from app.graph.state import AgentState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle chat message and return AI response.
    Loads conversation history from checkpointer if conversation_id exists.
    """
    logger.info("=" * 80)
    logger.info(f"CHAT REQUEST RECEIVED - Message: '{request.message}'")
    logger.info(f"Conversation ID: {request.conversation_id}")
    try:
        # Get or create conversation
        if request.conversation_id:
            result = await db.execute(
                select(Conversation).where(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == current_user.id
                )
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            conversation = Conversation(user_id=current_user.id)
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        await db.commit()
        
        # Load user's recipients and occasions from database
        recipients_result = await db.execute(
            select(Recipient).where(Recipient.user_id == current_user.id)
        )
        recipients = recipients_result.scalars().all()
        
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
        
        user_recipients = [
            {
                "id": str(r.id),
                "name": r.name,
                "relationship": r.relationship_type,
                "age_band": r.age_band,
                "interests": r.interests or [],
                "constraints": r.constraints or [],
                "notes": r.notes,
                "street_address": r.street_address,
                "city": r.city,
                "state_province": r.state_province,
                "postal_code": r.postal_code,
                "country": r.country,
                "address_validation_status": r.address_validation_status,
                "is_core_contact": r.is_core_contact,
                "network_level": r.network_level,
                "relationships": relationships_map.get(str(r.id), [])
            }
            for r in recipients
        ]
        
        occasions_result = await db.execute(
            select(Occasion).where(Occasion.user_id == current_user.id)
        )
        occasions = occasions_result.scalars().all()
        user_occasions = [
            {
                "id": str(o.id),
                "recipient_id": str(o.recipient_id),
                "name": o.name,
                "occasion_type": o.occasion_type,
                "date": str(o.date) if o.date else None,
                "budget_range": o.budget_range,
                "status": o.status.value if o.status else None
            }
            for o in occasions
        ]
        
        # Load conversation history from checkpointer if conversation exists
        config = {"configurable": {"thread_id": str(conversation.id)}}
        existing_state = None
        if request.conversation_id:
            try:
                # Try to load existing state from checkpointer
                checkpoint_state = await my3_graph.aget_state(config)
                if checkpoint_state and checkpoint_state.values:
                    existing_state = checkpoint_state.values
                    logger.info(f"Loaded existing conversation state for {conversation.id}")
            except Exception as e:
                logger.warning(f"Could not load conversation state: {e}")
        
        # Prepare state for LangGraph
        # If existing state exists, merge with new message
        if existing_state:
            # Add new user message to existing messages
            messages = existing_state.get("messages", [])
            messages.append(HumanMessage(content=request.message))
            state: AgentState = {
                **existing_state,
                "messages": messages,
                "user_recipients": user_recipients,  # Refresh from DB
                "user_occasions": user_occasions,  # Refresh from DB
            }
        else:
            state: AgentState = {
                "messages": [HumanMessage(content=request.message)],
                "user_id": str(current_user.id),
                "conversation_id": str(conversation.id),
                "user_recipients": user_recipients,
                "user_occasions": user_occasions,
                "current_intent": None,
                "detected_person": None,
                "recipient_exists": None,
                "matched_recipient_id": None,
                "pending_actions": [],
                "requires_confirmation": False,
                "confirmation_prompt": None,
                "ai_response": None,
                "gift_ideas": None,
                "error": None
            }
        
        # Run workflow with config (required for checkpointer)
        logger.info(f"Invoking workflow for conversation {conversation.id}")
        logger.info(f"User message: {request.message}")
        logger.info(f"User ID: {current_user.id}, Email: {current_user.email}")
        result = await my3_graph.ainvoke(state, config)
        
        # Extract response data
        ai_response = result.get("ai_response") or (
            result["messages"][-1].content if result.get("messages") else "I'm here to help!"
        )
        
        # Only include gift_ideas if intent is gift_search
        # This prevents showing gift suggestions during casual chat, add_recipient, or update_info
        current_intent = result.get("current_intent")
        gift_ideas = result.get("gift_ideas") if current_intent == "gift_search" else None
        
        requires_confirmation = result.get("requires_confirmation", False)
        confirmation_prompt = result.get("confirmation_prompt")
        
        # Save AI message
        ai_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            metadata={
                "gift_ideas": gift_ideas,
                "requires_confirmation": requires_confirmation,
                "confirmation_prompt": confirmation_prompt
            } if gift_ideas or requires_confirmation else None
        )
        db.add(ai_message)
        await db.commit()
        
        logger.info(f"Chat response generated for conversation {conversation.id}")
        logger.info(f"AI Response: {ai_response[:200]}...")  # First 200 chars
        logger.info(f"Requires confirmation: {requires_confirmation}")
        logger.info(f"Pending actions: {len(result.get('pending_actions', []))} actions")
        logger.info("=" * 80)
        
        return ChatResponse(
            response=ai_response,
            gift_ideas=gift_ideas,
            requires_confirmation=requires_confirmation,
            confirmation_prompt=confirmation_prompt,
            conversation_id=conversation.id,
            metadata={
                "intent": result.get("current_intent"),
                "detected_person": result.get("detected_person"),
                "pending_actions": result.get("pending_actions", [])
            } if result.get("current_intent") else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.post("/confirm", response_model=ChatConfirmResponse)
async def confirm_action(
    request: ChatConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm an action (e.g., add recipient, update info).
    Loads conversation state from checkpointer and executes pending actions if confirmed.
    """
    try:
        # Verify conversation belongs to user
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Load conversation state from checkpointer
        config = {"configurable": {"thread_id": str(conversation.id)}}
        checkpoint_state = await my3_graph.aget_state(config)
        
        if not checkpoint_state or not checkpoint_state.values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation state not found"
            )
        
        state = checkpoint_state.values
        pending_actions = state.get("pending_actions", [])
        
        if not pending_actions:
            return ChatConfirmResponse(
                message="No pending actions to confirm."
            )
        
        if not request.confirmed:
            # Clear pending actions and return acknowledgment
            logger.info(f"User declined confirmation for conversation {conversation.id}")
            return ChatConfirmResponse(
                message="Action cancelled. No changes were made."
            )
        
        # Execute pending actions
        logger.info(f"Executing {len(pending_actions)} pending actions for conversation {conversation.id}")
        created_recipient = None
        created_occasion = None
        
        for action in pending_actions:
            action_type = action.get("type")
            
            if action_type == "create_recipient":
                # Create recipient
                person_data = action.get("data", {})
                recipient_name = person_data.get("name", "").strip()
                recipient_relationship = person_data.get("relationship")
                
                if not recipient_name:
                    logger.warning("Skipping create_recipient action - missing name")
                    continue
                
                # CRITICAL: Check for duplicates before creating
                # Check for exact name match (case-insensitive)
                existing_recipient_result = await db.execute(
                    select(Recipient).where(
                        Recipient.user_id == current_user.id,
                        func.lower(Recipient.name) == func.lower(recipient_name)
                    )
                )
                existing_recipient = existing_recipient_result.scalar_one_or_none()
                
                if existing_recipient:
                    logger.warning(f"Duplicate recipient detected: '{recipient_name}' already exists (ID: {existing_recipient.id}). Skipping creation.")
                    # Instead of creating, update the existing recipient with new information
                    updated = False
                    if person_data.get("interests"):
                        existing_interests = existing_recipient.interests or []
                        new_interests = person_data.get("interests", [])
                        existing_recipient.interests = list(set(existing_interests + new_interests))
                        updated = True
                    if person_data.get("notes"):
                        existing_notes = existing_recipient.notes or ""
                        new_notes = person_data.get("notes", "")
                        if existing_notes and new_notes:
                            if existing_notes.lower() not in new_notes.lower():
                                existing_recipient.notes = f"{existing_notes}. {new_notes}"
                            else:
                                existing_recipient.notes = new_notes
                        else:
                            existing_recipient.notes = new_notes
                        updated = True
                    if person_data.get("age_band") and not existing_recipient.age_band:
                        existing_recipient.age_band = person_data.get("age_band")
                        updated = True
                    if person_data.get("street_address") and not existing_recipient.street_address:
                        existing_recipient.street_address = person_data.get("street_address")
                        existing_recipient.city = person_data.get("city")
                        existing_recipient.state_province = person_data.get("state_province")
                        existing_recipient.postal_code = person_data.get("postal_code")
                        existing_recipient.country = person_data.get("country")
                        updated = True
                    
                    if updated:
                        # Validate address if updated
                        if existing_recipient.street_address and existing_recipient.city:
                            from app.services.address_validator import validate_address
                            import json
                            validation_result = await validate_address(
                                street=existing_recipient.street_address,
                                city=existing_recipient.city,
                                state=existing_recipient.state_province,
                                postal_code=existing_recipient.postal_code,
                                country=existing_recipient.country
                            )
                            existing_recipient.address_validation_status = validation_result.get("status", "unvalidated")
                            if validation_result.get("normalized_address"):
                                existing_recipient.validated_address_json = json.dumps(validation_result["normalized_address"])
                        
                        await db.commit()
                        await db.refresh(existing_recipient)
                        logger.info(f"Updated existing recipient {existing_recipient.id} instead of creating duplicate")
                    
                    created_recipient = {
                        "id": str(existing_recipient.id),
                        "name": existing_recipient.name,
                        "relationship": existing_recipient.relationship_type,
                        "age_band": existing_recipient.age_band,
                        "interests": existing_recipient.interests or [],
                        "constraints": existing_recipient.constraints or [],
                        "notes": existing_recipient.notes,
                        "street_address": existing_recipient.street_address,
                        "city": existing_recipient.city,
                        "state_province": existing_recipient.state_province,
                        "postal_code": existing_recipient.postal_code,
                        "country": existing_recipient.country,
                        "address_validation_status": existing_recipient.address_validation_status
                    }
                    continue  # Skip to next action
                
                # No duplicate found, proceed with creation
                new_recipient = Recipient(
                    user_id=current_user.id,
                    name=recipient_name,
                    relationship_type=recipient_relationship,
                    age_band=person_data.get("age_band"),
                    interests=person_data.get("interests", []),
                    constraints=person_data.get("constraints", []),
                    notes=person_data.get("notes"),
                    street_address=person_data.get("street_address"),
                    city=person_data.get("city"),
                    state_province=person_data.get("state_province"),
                    postal_code=person_data.get("postal_code"),
                    country=person_data.get("country")
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
                
                created_recipient = {
                    "id": str(new_recipient.id),
                    "name": new_recipient.name,
                    "relationship": new_recipient.relationship_type,
                    "age_band": new_recipient.age_band,
                    "interests": new_recipient.interests or [],
                    "constraints": new_recipient.constraints or [],
                    "notes": new_recipient.notes,
                    "street_address": new_recipient.street_address,
                    "city": new_recipient.city,
                    "state_province": new_recipient.state_province,
                    "postal_code": new_recipient.postal_code,
                    "country": new_recipient.country,
                    "address_validation_status": new_recipient.address_validation_status
                }
                logger.info(f"Created recipient {new_recipient.id} for user {current_user.id}")
                
                # If occasion_data is provided, create the occasion after recipient is created
                occasion_data = action.get("occasion_data")
                if occasion_data:
                    from datetime import datetime as dt
                    occasion_date = None
                    if occasion_data.get("date"):
                        try:
                            # Try to parse natural language dates
                            date_str = occasion_data["date"]
                            # Try ISO format first
                            try:
                                occasion_date = dt.fromisoformat(date_str.replace("Z", "+00:00")).date()
                            except:
                                # Try parsing natural language dates (basic support)
                                # This is a simplified parser - you might want to use dateutil for better parsing
                                import re
                                # Match patterns like "April 16", "June 30th", "November 1st"
                                month_map = {
                                    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
                                    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
                                }
                                date_str_lower = date_str.lower()
                                for month_name, month_num in month_map.items():
                                    if month_name in date_str_lower:
                                        # Extract day number
                                        day_match = re.search(r'(\d+)', date_str)
                                        if day_match:
                                            day = int(day_match.group(1))
                                            # For birthdays/anniversaries (recurring events), use a reference year
                                            # If the date has passed this year, use next year to keep it "upcoming"
                                            from datetime import date
                                            today = date.today()
                                            current_year = today.year
                                            
                                        # Try current year first
                                        try:
                                            test_date = date(current_year, month_num, day)
                                            # If date has passed this year, use next year
                                            if test_date < today:
                                                occasion_date = date(current_year + 1, month_num, day)
                                            else:
                                                occasion_date = test_date
                                        except ValueError:
                                            # Invalid date for current year (e.g., Feb 30, or leap year issue)
                                            # Try next year
                                            try:
                                                occasion_date = date(current_year + 1, month_num, day)
                                            except ValueError:
                                                # Still invalid, skip this date
                                                logger.warning(f"Invalid date: {month_num}/{day}")
                                                pass
                                            break
                        except Exception as e:
                            logger.warning(f"Could not parse occasion date '{occasion_data.get('date')}': {e}")
                    
                    new_occasion = Occasion(
                        user_id=current_user.id,
                        recipient_id=new_recipient.id,
                        name=occasion_data.get("name", "Birthday"),
                        occasion_type=occasion_data.get("occasion_type", "birthday"),
                        date=occasion_date,
                        budget_range=occasion_data.get("budget_range"),
                        status=OccasionStatus.IDEA_NEEDED
                    )
                    db.add(new_occasion)
                    await db.commit()
                    await db.refresh(new_occasion)
                    
                    created_occasion = {
                        "id": str(new_occasion.id),
                        "recipient_id": str(new_occasion.recipient_id),
                        "name": new_occasion.name,
                        "occasion_type": new_occasion.occasion_type,
                        "date": str(new_occasion.date) if new_occasion.date else None,
                        "budget_range": new_occasion.budget_range,
                        "status": new_occasion.status.value if new_occasion.status else None
                    }
                    logger.info(f"Created occasion {new_occasion.id} for recipient {new_recipient.id}")
            
            elif action_type == "update_recipient":
                recipient_id = action.get("recipient_id")
                if not recipient_id:
                    continue
                
                # Find recipient
                recipient_result = await db.execute(
                    select(Recipient).where(
                        Recipient.id == UUID(recipient_id),
                        Recipient.user_id == current_user.id
                    )
                )
                recipient = recipient_result.scalar_one_or_none()
                
                if not recipient:
                    logger.warning(f"Recipient {recipient_id} not found for update")
                    continue
                
                # Update recipient with new data
                person_data = action.get("data", {})
                if person_data.get("name"):
                    recipient.name = person_data["name"]
                if person_data.get("relationship"):
                    recipient.relationship_type = person_data["relationship"]
                if person_data.get("age_band"):
                    recipient.age_band = person_data["age_band"]
                if person_data.get("interests"):
                    # Merge interests (append new ones)
                    existing_interests = recipient.interests or []
                    new_interests = person_data["interests"]
                    recipient.interests = list(set(existing_interests + new_interests))
                
                # Handle address fields
                address_changed = False
                if person_data.get("street_address") is not None:
                    recipient.street_address = person_data["street_address"]
                    address_changed = True
                if person_data.get("city") is not None:
                    recipient.city = person_data["city"]
                    address_changed = True
                if person_data.get("state_province") is not None:
                    recipient.state_province = person_data["state_province"]
                    address_changed = True
                if person_data.get("postal_code") is not None:
                    recipient.postal_code = person_data["postal_code"]
                    address_changed = True
                if person_data.get("country") is not None:
                    recipient.country = person_data["country"]
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
                if person_data.get("constraints"):
                    # Merge constraints
                    existing_constraints = recipient.constraints or []
                    new_constraints = person_data["constraints"]
                    recipient.constraints = list(set(existing_constraints + new_constraints))
                if person_data.get("notes"):
                    # Merge notes: append new information to existing notes if they exist
                    existing_notes = recipient.notes or ""
                    new_notes = person_data["notes"]
                    if existing_notes and new_notes:
                        # Check if new notes already contain existing info to avoid duplication
                        if existing_notes.lower() not in new_notes.lower():
                            recipient.notes = f"{existing_notes}. {new_notes}"
                        else:
                            # New notes already contains existing info, just replace
                            recipient.notes = new_notes
                    else:
                        recipient.notes = new_notes
                
                await db.commit()
                await db.refresh(recipient)
                
                created_recipient = {
                    "id": str(recipient.id),
                    "name": recipient.name,
                    "relationship": recipient.relationship_type,
                    "age_band": recipient.age_band,
                    "interests": recipient.interests or [],
                    "constraints": recipient.constraints or [],
                    "notes": recipient.notes,
                    "street_address": recipient.street_address,
                    "city": recipient.city,
                    "state_province": recipient.state_province,
                    "postal_code": recipient.postal_code,
                    "country": recipient.country,
                    "address_validation_status": recipient.address_validation_status
                }
                logger.info(f"Updated recipient {recipient.id}")
            
            elif action_type == "create_secondary_contact":
                primary_recipient_id = action.get("primary_recipient_id")
                secondary_contact_data = action.get("secondary_contact", {})
                is_bidirectional = action.get("is_bidirectional", False)
                
                if not primary_recipient_id or not secondary_contact_data:
                    continue
                
                # Verify primary recipient exists and belongs to user
                primary_result = await db.execute(
                    select(Recipient).where(
                        Recipient.id == UUID(primary_recipient_id),
                        Recipient.user_id == current_user.id
                    )
                )
                primary_recipient = primary_result.scalar_one_or_none()
                
                if not primary_recipient:
                    logger.warning(f"Primary recipient {primary_recipient_id} not found")
                    continue
                
                # Check if secondary contact already exists
                secondary_name = secondary_contact_data.get("name")
                existing_secondary_result = await db.execute(
                    select(Recipient).where(
                        Recipient.user_id == current_user.id,
                        Recipient.name.ilike(f"%{secondary_name}%")
                    )
                )
                existing_secondary = existing_secondary_result.scalar_one_or_none()
                
                if existing_secondary:
                    # Secondary contact exists, just create relationship
                    secondary_recipient = existing_secondary
                else:
                    # Create new secondary contact
                    secondary_recipient = Recipient(
                        user_id=current_user.id,
                        name=secondary_name,
                        relationship_type=secondary_contact_data.get("relationship_type"),
                        is_core_contact=secondary_contact_data.get("is_core_contact", False),
                        network_level=secondary_contact_data.get("network_level", 2)
                    )
                    db.add(secondary_recipient)
                    await db.commit()
                    await db.refresh(secondary_recipient)
                    logger.info(f"Created secondary contact {secondary_recipient.id} ({secondary_recipient.name})")
                
                # Create relationship
                relationship = RecipientRelationship(
                    user_id=current_user.id,
                    from_recipient_id=UUID(primary_recipient_id),
                    to_recipient_id=secondary_recipient.id,
                    relationship_type=secondary_contact_data.get("relationship_type", ""),
                    is_bidirectional=is_bidirectional
                )
                db.add(relationship)
                
                # If bidirectional, create reverse relationship
                if is_bidirectional:
                    reverse_relationship_type = "husband" if secondary_contact_data.get("relationship_type") == "wife" else "wife"
                    reverse_relationship = RecipientRelationship(
                        user_id=current_user.id,
                        from_recipient_id=secondary_recipient.id,
                        to_recipient_id=UUID(primary_recipient_id),
                        relationship_type=reverse_relationship_type,
                        is_bidirectional=True
                    )
                    db.add(reverse_relationship)
                
                await db.commit()
                logger.info(f"Created relationship: {primary_recipient.name} -> {secondary_recipient.name} ({secondary_contact_data.get('relationship_type')})")
            
            elif action_type == "create_relationship":
                from_recipient_id = action.get("from_recipient_id")
                to_recipient_id = action.get("to_recipient_id")
                relationship_type = action.get("relationship_type")
                is_bidirectional = action.get("is_bidirectional", False)
                
                if not from_recipient_id or not to_recipient_id or not relationship_type:
                    continue
                
                # Verify both recipients exist and belong to user
                from_result = await db.execute(
                    select(Recipient).where(
                        Recipient.id == UUID(from_recipient_id),
                        Recipient.user_id == current_user.id
                    )
                )
                to_result = await db.execute(
                    select(Recipient).where(
                        Recipient.id == UUID(to_recipient_id),
                        Recipient.user_id == current_user.id
                    )
                )
                from_recipient = from_result.scalar_one_or_none()
                to_recipient = to_result.scalar_one_or_none()
                
                if not from_recipient or not to_recipient:
                    logger.warning(f"Recipients not found for relationship: {from_recipient_id} -> {to_recipient_id}")
                    continue
                
                # Check if relationship already exists
                existing_result = await db.execute(
                    select(RecipientRelationship).where(
                        RecipientRelationship.user_id == current_user.id,
                        RecipientRelationship.from_recipient_id == UUID(from_recipient_id),
                        RecipientRelationship.to_recipient_id == UUID(to_recipient_id)
                    )
                )
                existing_relationship = existing_result.scalar_one_or_none()
                
                if not existing_relationship:
                    relationship = RecipientRelationship(
                        user_id=current_user.id,
                        from_recipient_id=UUID(from_recipient_id),
                        to_recipient_id=UUID(to_recipient_id),
                        relationship_type=relationship_type,
                        is_bidirectional=is_bidirectional
                    )
                    db.add(relationship)
                    
                    # If bidirectional, create reverse relationship
                    if is_bidirectional:
                        reverse_relationship_type = "husband" if relationship_type == "wife" else "wife"
                        reverse_relationship = RecipientRelationship(
                            user_id=current_user.id,
                            from_recipient_id=UUID(to_recipient_id),
                            to_recipient_id=UUID(from_recipient_id),
                            relationship_type=reverse_relationship_type,
                            is_bidirectional=True
                        )
                        db.add(reverse_relationship)
                    
                    await db.commit()
                    logger.info(f"Created relationship: {from_recipient.name} -> {to_recipient.name} ({relationship_type})")
            
            elif action_type == "delete_recipient":
                recipient_id = action.get("recipient_id")
                if not recipient_id:
                    continue
                
                # Verify recipient exists and belongs to user
                recipient_result = await db.execute(
                    select(Recipient).where(
                        Recipient.id == UUID(recipient_id),
                        Recipient.user_id == current_user.id
                    )
                )
                recipient = recipient_result.scalar_one_or_none()
                
                if not recipient:
                    logger.warning(f"Recipient {recipient_id} not found or doesn't belong to user")
                    continue
                
                recipient_name = recipient.name
                # Delete recipient (cascade will handle occasions, relationships, etc.)
                await db.delete(recipient)
                await db.commit()
                logger.info(f"Deleted recipient {recipient_id} ({recipient_name}) for user {current_user.id}")
            
            elif action_type == "create_occasion":
                recipient_id = action.get("recipient_id")
                occasion_data = action.get("occasion_data", {})
                
                if not recipient_id:
                    continue
                
                # Verify recipient belongs to user
                recipient_result = await db.execute(
                    select(Recipient).where(
                        Recipient.id == UUID(recipient_id),
                        Recipient.user_id == current_user.id
                    )
                )
                recipient = recipient_result.scalar_one_or_none()
                
                if not recipient:
                    logger.warning(f"Recipient {recipient_id} not found for occasion creation")
                    continue
                
                # Create occasion
                from datetime import datetime as dt, date
                import re
                occasion_date = None
                if occasion_data.get("date"):
                    try:
                        date_str = occasion_data["date"]
                        # Try ISO format first
                        try:
                            occasion_date = dt.fromisoformat(date_str.replace("Z", "+00:00")).date()
                        except:
                            # Try parsing natural language dates
                            month_map = {
                                "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
                                "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
                            }
                            date_str_lower = date_str.lower()
                            for month_name, month_num in month_map.items():
                                if month_name in date_str_lower:
                                    # Extract day number
                                    day_match = re.search(r'(\d+)', date_str)
                                    if day_match:
                                        day = int(day_match.group(1))
                                        # For birthdays/anniversaries (recurring events), use a reference year
                                        # If the date has passed this year, use next year to keep it "upcoming"
                                        today = date.today()
                                        current_year = today.year
                                        
                                        # Try current year first
                                        try:
                                            test_date = date(current_year, month_num, day)
                                            # If date has passed this year, use next year
                                            if test_date < today:
                                                occasion_date = date(current_year + 1, month_num, day)
                                            else:
                                                occasion_date = test_date
                                        except ValueError:
                                            # Invalid date for current year (e.g., Feb 30, or leap year issue)
                                            # Try next year
                                            try:
                                                occasion_date = date(current_year + 1, month_num, day)
                                            except ValueError:
                                                # Still invalid, skip this date
                                                logger.warning(f"Invalid date: {month_num}/{day}")
                                                pass
                                        break
                    except Exception as e:
                        logger.warning(f"Could not parse occasion date '{occasion_data.get('date')}': {e}")
                
                new_occasion = Occasion(
                    user_id=current_user.id,
                    recipient_id=UUID(recipient_id),
                    name=occasion_data.get("name", ""),
                    occasion_type=occasion_data.get("occasion_type"),
                    date=occasion_date,
                    budget_range=occasion_data.get("budget_range"),
                    status=OccasionStatus.IDEA_NEEDED
                )
                db.add(new_occasion)
                await db.commit()
                await db.refresh(new_occasion)
                
                created_occasion = {
                    "id": str(new_occasion.id),
                    "recipient_id": str(new_occasion.recipient_id),
                    "name": new_occasion.name,
                    "occasion_type": new_occasion.occasion_type,
                    "date": str(new_occasion.date) if new_occasion.date else None,
                    "budget_range": new_occasion.budget_range,
                    "status": new_occasion.status.value if new_occasion.status else None
                }
                logger.info(f"Created occasion {new_occasion.id}")
        
        # Clear pending actions in state
        # Note: We can't directly modify checkpoint state, but the next chat message will start fresh
        # The pending_actions will be cleared naturally when the workflow runs again
        
        # Save confirmation message
        confirmation_message = Message(
            conversation_id=conversation.id,
            role="system",
            content=f"User confirmed action: {', '.join([a.get('type', 'unknown') for a in pending_actions])}"
        )
        db.add(confirmation_message)
        await db.commit()
        
        success_message = "Action confirmed successfully!"
        if created_recipient:
            success_message += f" {'Added' if action_type == 'create_recipient' else 'Updated'} {created_recipient['name']} to your network."
        if created_occasion:
            success_message += f" Created occasion: {created_occasion['name']}."
        
        logger.info(f"Confirmed actions for conversation {conversation.id}")
        
        return ChatConfirmResponse(
            message=success_message,
            recipient=created_recipient,
            occasion=created_occasion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in confirm endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm action"
        )

