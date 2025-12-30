from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging
from difflib import SequenceMatcher

from app.graph.state import AgentState
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)

# Pydantic models for structured output
class IntentClassification(BaseModel):
    """Intent classification result."""
    intent: str = Field(description="One of: gift_search, add_recipient, update_info, casual_chat, unclear")
    confidence: float = Field(description="Confidence score 0-1", ge=0, le=1)


class PersonInfo(BaseModel):
    """Extracted person information."""
    name: Optional[str] = Field(None, description="Person's name")
    relationship: Optional[str] = Field(None, description="Relationship type (mom, dad, wife, friend, etc.)")
    interests: List[str] = Field(default_factory=list, description="List of interests, hobbies, or preferences")
    age_band: Optional[str] = Field(None, description="Age range or band (e.g., '30s', '50-60')")
    notes: Optional[str] = Field(None, description="Additional notes or information (e.g., family members, personal details, constraints)")
    occasion_name: Optional[str] = Field(None, description="Occasion name (e.g., 'Birthday', 'Anniversary', 'Christmas')")
    occasion_date: Optional[str] = Field(None, description="Occasion date in ISO format (YYYY-MM-DD) or natural language (e.g., 'April 16', 'June 30th', 'November 1st')")
    secondary_contacts: List[dict] = Field(default_factory=list, description="List of secondary contacts mentioned (e.g., [{'name': 'Archana', 'relationship_to_primary': 'wife'}])")
    # Address fields
    street_address: Optional[str] = Field(None, description="Street address (e.g., '123 Main St', '456 Oak Avenue')")
    city: Optional[str] = Field(None, description="City name (e.g., 'New York', 'Los Angeles')")
    state_province: Optional[str] = Field(None, description="State or province (e.g., 'NY', 'California', 'ON')")
    postal_code: Optional[str] = Field(None, description="Postal code or ZIP code (e.g., '10001', '90210', 'K1A 0B1')")
    country: Optional[str] = Field(None, description="Country name or code (e.g., 'US', 'USA', 'United States', 'Canada')")


class GiftIdea(BaseModel):
    """Gift idea structure."""
    title: str = Field(description="Gift title/name")
    description: str = Field(description="Detailed description")
    price: str = Field(description="Price or price range (e.g., '$50', '$20-30')")
    category: str = Field(description="Gift category (e.g., 'electronics', 'books', 'experiences')")
    url: Optional[str] = Field(None, description="Product URL if available")


class GiftIdeasList(BaseModel):
    """List of gift ideas."""
    gift_ideas: List[GiftIdea] = Field(description="List of 5 personalized gift ideas")


def _fuzzy_match_name(name1: str, name2: str, threshold: float = 0.8) -> bool:
    """Check if two names are similar using fuzzy matching."""
    if not name1 or not name2:
        return False
    similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
    return similarity >= threshold


async def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Classify user intent using ChatOpenAI with structured output.
    Returns: {"current_intent": str}
    """
    try:
        messages = state.get("messages", [])
        if not messages:
            return {"current_intent": "unclear", "error": "No messages in state"}
        
        # Get the last user message
        last_message = messages[-1]
        user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Create prompt for intent classification
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for a gift recommendation assistant.
Classify the user's intent into one of these categories:
- gift_search: User explicitly wants gift ideas, recommendations, or suggestions for someone
- add_recipient: User wants to add a new person to their network (providing info about someone new)
- update_info: User wants to update or correct information about an existing person
- casual_chat: General conversation, greetings, questions, or providing information without explicit action request
- unclear: Intent is unclear or ambiguous

IMPORTANT RULES:
1. gift_search: Classify as "gift_search" if the user asks for gift ideas, suggestions, or recommendations. 
   - ANY message containing "suggest" + "gift" → ALWAYS gift_search
   - ANY message containing "gift" + "idea" → ALWAYS gift_search
   - ANY message asking "what should I get/buy" or "what to get/buy" → ALWAYS gift_search
   - ANY message asking "what should I buy/purchase for [name]" → ALWAYS gift_search
   - Variations that indicate gift_search:
     * "what should I get" / "what should I buy" / "what to get" / "what to buy"
     * "suggest" + "gift" / "gifts"
     * "find" + "gift" / "gifts" (e.g., "find gift for [name]")
     * "gift ideas" / "gift recommendations"
     * "buy for" / "purchase for" (when asking about a person)
   - Examples:
     * "What gift should I get for mom?" → gift_search
     * "What should I buy for Anuradha this new years day?" → gift_search (MUST be gift_search)
     * "What should i buy for Anuradha this new years day?" → gift_search (MUST be gift_search)
     * "Gift ideas for my sister" → gift_search
     * "Suggest something for her birthday" → gift_search
     * "Suggest gifts for Anuradha for new years day" → gift_search (MUST be gift_search)
     * "Suggest gifts for Anuradha on new years day" → gift_search (MUST be gift_search)
     * "Suggest gifts for [name] for [occasion]" → gift_search (MUST be gift_search)
     * "Suggest gifts for [name] on [occasion]" → gift_search (MUST be gift_search)
     * "What should I get for [name]?" → gift_search
     * "What should I buy for [name]?" → gift_search
     * "Find gift for [name]" → gift_search (MUST be gift_search)
     * "Find gifts for [name]" → gift_search (MUST be gift_search)
   - CRITICAL: If the message asks what to buy/get/purchase/find for someone, it MUST be classified as gift_search, NOT casual_chat or unclear
   - DO NOT classify as gift_search if they're just mentioning birthdays or occasions without asking for gifts

2. add_recipient: Classify when user provides information about a NEW person (name, relationship, interests, birthday, etc.)
   - "Manasa Veena is my other sister. Her birthday is Nov 1" → add_recipient
   - "Add my wife Ritika" → add_recipient
   - "My mom loves gardening" → add_recipient (if mom is not in network)
   - "[Name] likes [interest]" → add_recipient (if person is NOT in network - new person)
   - NOTE: If user says "[Name]'s birthday is [date]" and the name sounds like it might be an existing person, prefer "update_info" over "add_recipient"
   - NOTE: If user says "[Name] likes [interest]" and the person exists in network, use "update_info" instead

3. update_info: Classify when user wants to update/correct information about someone already in their network
   - "Update Ritika's interests" → update_info
   - "Ritika's birthday is actually March 15th" → update_info (if Ritika exists)
   - "Ritika likes Old Hindi Music" → update_info (if Ritika exists - adding/updating interests)
   - "[Name] likes [interest]" → update_info (if person exists - adding interests)
   - "[Name] loves [interest]" → update_info (if person exists - adding interests)
   - "Anuradha is 6 years old" → update_info (if Anuradha exists - updating age)
   - "Anu is 6 years old" → update_info (if Anu/Anuradha exists - updating age)
   - "Ravis wife is Archana" → update_info (if Ravi exists - adding relationship info)
   - "Ramesh Naidus wife name is Swetha" → update_info (if Ramesh Naidu exists - adding relationship info)
   - IMPORTANT: When user provides interests, likes, or preferences for an existing person (e.g., "Ritika likes music"), classify as update_info, NOT casual_chat or unclear

4. casual_chat: General questions, greetings, or informational statements that don't require action
   - "Hello" → casual_chat
   - "What do you know about Ritika?" → casual_chat
   - "Who is Ritika?" → casual_chat
   - "Who is [name]?" → casual_chat (questions about people in the network)
   - "When is my wife's birthday?" → casual_chat

Examples:
- "Add my wife Ritika" → add_recipient
- "Add my cousin Seshu to the network" → add_recipient
- "Manasa Veena is my other sister. Her birthday is Nov 1" → add_recipient
- "Gift ideas for mom" → gift_search
- "What should I get for my sister?" → gift_search
- "What should I buy for Anuradha this new years day?" → gift_search
- "What should i buy for Anuradha this new years day?" → gift_search
- "Suggest gifts for Anuradha for new years day" → gift_search
- "Suggest gifts for John for his birthday" → gift_search
- "What gift should I get for Ritika?" → gift_search
- "What should I buy for Ritika?" → gift_search
- "Find gift for Ritika" → gift_search
- "Find gifts for Ritika" → gift_search
- "Find gifts for my wife" → gift_search
- "Update Ritika's interests" → update_info
- "Ritika likes Old Hindi Music" → update_info (if Ritika exists)
- "Ramesh Naidus wife is Swetha" → update_info (if Ramesh Naidu exists)
- "When is my wife's birthday?" → casual_chat
- "Who is Ritika?" → casual_chat
- "Do you know Visala?" → casual_chat"""),
            ("human", "{message}")
        ])
        
        # Get LLM with structured output
        llm = get_llm(temperature=0.3)
        structured_llm = llm.with_structured_output(IntentClassification)
        
        # Invoke LLM
        result = await structured_llm.ainvoke(prompt.format_messages(message=user_message))
        
        intent = result.intent
        logger.info(f"=== ROUTER NODE ===")
        logger.info(f"User message: '{user_message}'")
        logger.info(f"Intent classified by LLM: {intent} (confidence: {result.confidence})")
        
        # Fallback: If LLM misclassifies but message clearly contains gift request keywords, override to gift_search
        user_message_lower = user_message.lower()
        
        # Check for gift request patterns - comprehensive list
        has_gift = "gift" in user_message_lower or "gifts" in user_message_lower
        has_suggest = "suggest" in user_message_lower
        has_find = "find" in user_message_lower
        has_buy = "buy" in user_message_lower
        has_get = "get" in user_message_lower
        has_for = "for" in user_message_lower
        has_what = "what" in user_message_lower
        has_should = "should" in user_message_lower
        has_gift_ideas = "gift idea" in user_message_lower or "gift ideas" in user_message_lower
        
        logger.info(f"Pattern check - has_gift: {has_gift}, has_suggest: {has_suggest}, has_find: {has_find}, has_buy: {has_buy}, has_get: {has_get}, has_for: {has_for}")
        
        # Determine if this is clearly a gift request
        is_gift_request = False
        
        # Pattern 1: "suggest" + "gift"/"gifts"
        if has_suggest and has_gift:
            is_gift_request = True
            logger.info(f"✓ Detected gift request pattern: 'suggest' + 'gift'/'gifts'")
        # Pattern 2: "find" + "gift"/"gifts" + "for" (e.g., "Find gifts for my wife")
        elif has_find and has_gift and has_for:
            is_gift_request = True
            logger.info(f"✓ Detected gift request pattern: 'find gift/gifts for'")
        # Pattern 2b: "find" + "gift"/"gifts" (even without "for", if it's clearly a gift request)
        elif has_find and has_gift:
            is_gift_request = True
            logger.info(f"✓ Detected gift request pattern: 'find gift/gifts'")
        # Pattern 3: "buy" + "for" (when asking about a person)
        elif has_buy and has_for:
            is_gift_request = True
            logger.info(f"✓ Detected gift request pattern: 'buy for'")
        # Pattern 4: "what should I get" + "for"
        elif has_what and has_should and has_get and has_for:
            is_gift_request = True
            logger.info(f"✓ Detected gift request pattern: 'what should I get for'")
        # Pattern 5: "gift ideas"
        elif has_gift_ideas:
            is_gift_request = True
            logger.info(f"✓ Detected gift request pattern: 'gift ideas'")
        
        logger.info(f"is_gift_request: {is_gift_request}, current intent: {intent}")
        
        # Override if it's clearly a gift request but misclassified
        if is_gift_request and intent != "gift_search":
            logger.warning(f"⚠️ LLM misclassified gift request as '{intent}' (confidence: {result.confidence}). Overriding to 'gift_search' based on keyword detection.")
            logger.warning(f"Original message: '{user_message}'")
            intent = "gift_search"
            logger.info(f"✓ Intent overridden to: {intent}")
        
        logger.info(f"Final intent returned: {intent}")
        logger.info(f"=== END ROUTER NODE ===")
        
        # Safety check: If intent is still unclear but message seems clear, log a warning
        if intent == "unclear":
            logger.warning(f"⚠️ Intent classified as 'unclear' for message: '{user_message}'. This might indicate a classification issue.")
            # Try to infer intent from message content as a last resort
            user_message_lower = user_message.lower()
            if "who is" in user_message_lower or "what do you know about" in user_message_lower:
                logger.warning(f"⚠️ Message appears to be a question about a person, but classified as unclear. Consider this as casual_chat.")
                # Don't override here - let it go to casual_chat handling which should work
            elif "find" in user_message_lower and ("gift" in user_message_lower or "gifts" in user_message_lower):
                logger.warning(f"⚠️ Message appears to be a gift search, but classified as unclear. This should have been caught by fallback.")
        
        return {"current_intent": intent}
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        logger.error(f"Error in router_node: {error_type}: {error_msg}", exc_info=True)
        logger.error(f"Error occurred while processing message: '{user_message if 'user_message' in locals() else 'unknown'}'")
        
        # Check for specific OpenAI API errors
        if "authentication" in error_msg.lower() or "invalid" in error_msg.lower() or "401" in error_msg:
            logger.error("[CRITICAL] OpenAI API Authentication Error - API key may be invalid or expired")
        elif "rate limit" in error_msg.lower() or "429" in error_msg or "insufficient_quota" in error_msg.lower():
            logger.error("[CRITICAL] OpenAI API Quota/Credit Exhausted - Account has run out of credits")
            logger.error("  -> This is why all requests are returning generic responses")
            logger.error("  -> Please add credits at https://platform.openai.com/account/billing")
        elif "insufficient" in error_msg.lower() or "quota" in error_msg.lower() or "credit" in error_msg.lower():
            logger.error("[CRITICAL] OpenAI API Credit/Quota Exhausted - Account has run out of credits")
            logger.error("  -> This is why all requests are returning generic responses")
            logger.error("  -> Please add credits at https://platform.openai.com/account/billing")
        elif "timeout" in error_msg.lower():
            logger.error("[WARNING] OpenAI API Timeout - Request took too long")
        
        return {"current_intent": "unclear", "error": str(e)}


async def extract_person_node(state: AgentState) -> Dict[str, Any]:
    """
    Extract person information from message using structured LLM output.
    Returns: {"detected_person": {name, relationship, interests, age_band}}
    """
    try:
        messages = state.get("messages", [])
        if not messages:
            return {"detected_person": None, "error": "No messages in state"}
        
        # Get conversation context
        conversation_text = "\n".join([
            msg.content if hasattr(msg, 'content') else str(msg)
            for msg in messages[-5:]  # Last 5 messages for context
        ])
        
        # Create prompt for person extraction
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract person information from the conversation.
Extract:
- name: Person's name if mentioned (e.g., "Ritika", "John", "Visala", "Mom")
  - Extract names from possessive forms: "Visala's birthday" → name: "Visala"
  - Extract names from direct mentions: "Ritika loves..." → name: "Ritika"
  - Be precise with names - don't confuse similar names
  - Pay attention to the MOST RECENT message for the person being discussed
- relationship: Relationship type (mom, dad, wife, husband, friend, sibling, sister, brother, cousin, colleague, coworker, etc.)
  - Handle possessive forms: "my wife" → "wife", "my mom" → "mom", "my friend" → "friend", "my cousin" → "cousin", "my colleague" → "colleague"
  - Handle direct mentions: "wife", "husband", "mother", "father", "sister", "brother", "cousin", "colleague", "coworker", etc.
- interests: List of interests, hobbies, or preferences mentioned
  - Extract from phrases like "likes [thing]", "loves [thing]", "interested in [thing]", etc.
  - Examples: "likes trading" → interests: ["trading"], "loves gardening and reading" → interests: ["gardening", "reading"]
- age_band: Age range or specific age if mentioned (e.g., "30s", "50-60", "elderly", "6 years old", "6", "25")
  - Extract specific ages: "6 years old" → age_band: "6 years old" or "6", "Anu is 6 years old" → age_band: "6 years old"
  - Extract age ranges: "30s" → age_band: "30s", "50-60" → age_band: "50-60"
- notes: Additional personal information, family details, or context
  - Extract ALL family information mentioned: "wife is Archana and Daughter is Midhuna" → notes: "Wife is Archana and Daughter is Midhuna"
  - Extract other personal details that don't fit into interests or age_band
  - IMPORTANT: When multiple pieces of family information are provided, extract ALL of them, not just one
  - Examples: 
    - "his sons name is Avyan Skanda" → notes: "Son's name: Avyan Skanda"
    - "wife is Archana and Daughter is Midhuna" → notes: "Wife is Archana and Daughter is Midhuna"
    - "Ravis wife is Archana and Daughter is Midhuna" → notes: "Wife is Archana and Daughter is Midhuna"
- occasion_name: Occasion type if mentioned (e.g., "Birthday", "Anniversary", "Christmas", "Wedding")
  - Extract from phrases like "birthday", "anniversary", "wedding", etc.
  - Default to "Birthday" if user mentions a date with a person's name
- occasion_date: Date of the occasion if mentioned
  - Extract dates in any format: "April 16", "June 30th", "November 1st", "2024-04-16", "4/16", etc.
  - Keep the original format as provided by the user (don't convert to ISO format yet)
- secondary_contacts: List of secondary contacts mentioned, with their relationship to the primary person
  - Extract when user mentions relationships between people: "[Person A]'s [relationship] is [Person B]" → secondary_contacts: [{{"name": "Person B", "relationship_to_primary": "relationship"}}]
  - Examples:
    - "Ramesh Naidus wife is Swetha" → name: "Ramesh Naidu", secondary_contacts: [{{"name": "Swetha", "relationship_to_primary": "wife"}}]
    - "Ravis wife is Archana and Daughter is Midhuna" → name: "Ravi", secondary_contacts: [{{"name": "Archana", "relationship_to_primary": "wife"}}, {{"name": "Midhuna", "relationship_to_primary": "daughter"}}]
    - "Ramesh naidu likes trading and his sons name is Avyan Skanda" → name: "Ramesh naidu", secondary_contacts: [{{"name": "Avyan Skanda", "relationship_to_primary": "son"}}]
  - IMPORTANT: Extract secondary_contacts when the message describes a relationship between two people, where one person is mentioned as having a relationship to another
  - The "primary" person is the one being discussed (the main subject), and "secondary" contacts are their family members/relationships
- address fields: Extract address information if mentioned
  - street_address: Street address (e.g., "123 Main St", "456 Oak Avenue", "789 Park Road")
  - city: City name (e.g., "New York", "Los Angeles", "Toronto")
  - state_province: State or province (e.g., "NY", "California", "ON", "Ontario")
  - postal_code: Postal code or ZIP code (e.g., "10001", "90210", "K1A 0B1")
  - country: Country name or code (e.g., "US", "USA", "United States", "Canada")
  - Extract from phrases like:
    * "lives at [address]" → extract full address
    * "address is [address]" → extract full address
    * "[name]'s address: [address]" → extract full address
    * "123 Main St, New York, NY 10001" → street_address: "123 Main St", city: "New York", state_province: "NY", postal_code: "10001"
    * "456 Oak Avenue, Los Angeles, CA 90210" → street_address: "456 Oak Avenue", city: "Los Angeles", state_province: "CA", postal_code: "90210"
  - Examples:
    * "Ritika lives at 123 Main St, New York, NY 10001" → street_address: "123 Main St", city: "New York", state_province: "NY", postal_code: "10001", country: "US"
    * "John's address is 456 Oak Avenue, Los Angeles, CA 90210" → street_address: "456 Oak Avenue", city: "Los Angeles", state_province: "CA", postal_code: "90210", country: "US"
    * "My mom lives in Toronto, ON, Canada" → city: "Toronto", state_province: "ON", country: "Canada"
  - If address is incomplete, extract what's available (e.g., just city and state)

IMPORTANT: 
- If a name is mentioned in the most recent message, extract it EXACTLY as written
- Don't confuse names from previous messages with the current message
- Focus on the person mentioned in the latest user message
- If birthday/occasion information is mentioned, extract both occasion_name and occasion_date

Examples:
- "Add my wife Ritika" → name: "Ritika", relationship: "wife", occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "Add my cousin Seshu to the network" → name: "Seshu", relationship: "cousin", occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "My colleague is Sandeep Mota. Add him to the network" → name: "Sandeep Mota", relationship: "colleague", occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "Visala's birthday is June 30th" → name: "Visala", relationship: None, occasion_name: "Birthday", occasion_date: "June 30th", notes: None, secondary_contacts: []
- "Ritikas birthday is on April 16" → name: "Ritika", relationship: None, occasion_name: "Birthday", occasion_date: "April 16", notes: None, secondary_contacts: []
- "My mom loves gardening" → relationship: "mom", interests: ["gardening"], occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "Anuradha is 6 years old" → name: "Anuradha", age_band: "6 years old", occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "Anu is 6 years old" → name: "Anu", age_band: "6 years old", occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "Ramesh naidu likes trading and his sons name is Avyan Skanda" → name: "Ramesh naidu", interests: ["trading"], notes: "Son's name: Avyan Skanda", secondary_contacts: [{{"name": "Avyan Skanda", "relationship_to_primary": "son"}}]
- "Ramesh Naidus wife is Swetha" → name: "Ramesh Naidu", relationship: None, interests: [], notes: None, secondary_contacts: [{{"name": "Swetha", "relationship_to_primary": "wife"}}]
- "Ravis wife is Archana and Daughter is Midhuna" → name: "Ravi", relationship: None, interests: [], notes: None, secondary_contacts: [{{"name": "Archana", "relationship_to_primary": "wife"}}, {{"name": "Midhuna", "relationship_to_primary": "daughter"}}]
- "Add John, he's my friend" → name: "John", relationship: "friend", occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "Update Ritika's interests" → name: "Ritika", relationship: None, occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "Ritika lives at 123 Main St, New York, NY 10001" → name: "Ritika", street_address: "123 Main St", city: "New York", state_province: "NY", postal_code: "10001", country: "US", occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []
- "John's address is 456 Oak Avenue, Los Angeles, CA 90210" → name: "John", street_address: "456 Oak Avenue", city: "Los Angeles", state_province: "CA", postal_code: "90210", country: "US", occasion_name: None, occasion_date: None, notes: None, secondary_contacts: []

If information is not mentioned, use None for that field.
Be accurate and extract information from both explicit statements and clear context."""),
            ("human", "{conversation}")
        ])
        
        # Get LLM with structured output
        llm = get_llm(temperature=0.3)
        structured_llm = llm.with_structured_output(PersonInfo)
        
        # Invoke LLM
        result = await structured_llm.ainvoke(prompt.format_messages(conversation=conversation_text))
        
        # Convert to dict and normalize relationship
        relationship = result.relationship
        if relationship:
            # Normalize relationship: remove "my" prefix, lowercase
            relationship = relationship.lower().replace("my ", "").strip()
            # Handle common variations
            relationship_map = {
                "mother": "mom",
                "father": "dad",
                "spouse": "wife" if "wife" in conversation_text.lower() else "husband",
                "partner": "wife" if "wife" in conversation_text.lower() else "husband"
            }
            relationship = relationship_map.get(relationship, relationship)
        
        detected_person = {
            "name": result.name,
            "relationship": relationship,
            "interests": result.interests or [],
            "age_band": result.age_band,
            "notes": result.notes,
            "occasion_name": result.occasion_name,
            "occasion_date": result.occasion_date,
            "secondary_contacts": result.secondary_contacts or [],
            "street_address": result.street_address,
            "city": result.city,
            "state_province": result.state_province,
            "postal_code": result.postal_code,
            "country": result.country
        }
        
        logger.info(f"Extracted person info: {detected_person} from conversation: {conversation_text[:100]}")
        
        return {"detected_person": detected_person}
        
    except Exception as e:
        logger.error(f"Error in extract_person_node: {e}", exc_info=True)
        return {"detected_person": None, "error": str(e)}


async def check_recipient_node(state: AgentState) -> Dict[str, Any]:
    """
    Check if detected_person exists in user_recipients.
    Match by name (exact first, then fuzzy) or relationship (exact).
    Returns: {
        "recipient_exists": bool, 
        "matched_recipient_id": str or None,
        "ambiguous_recipients": List[dict] or None  # When multiple people have same relationship
    }
    """
    try:
        detected_person = state.get("detected_person")
        user_recipients = state.get("user_recipients", [])
        
        if not detected_person:
            return {"recipient_exists": False, "matched_recipient_id": None}
        
        person_name = detected_person.get("name")
        person_relationship = detected_person.get("relationship")
        
        logger.info(f"Checking recipient match - name: {person_name}, relationship: {person_relationship}")
        logger.info(f"Available recipients: {[(r.get('name'), r.get('relationship')) for r in user_recipients]}")
        
        # Try to match by name (exact first, then fuzzy)
        if person_name:
            # Normalize name: lowercase, strip whitespace, remove extra spaces
            person_name_normalized = " ".join(person_name.lower().strip().split())
            
            # First try exact match (case-insensitive, normalized)
            for recipient in user_recipients:
                recipient_name = recipient.get("name", "")
                recipient_name_normalized = " ".join(recipient_name.lower().strip().split())
                if recipient_name_normalized == person_name_normalized:
                    logger.info(f"Matched recipient by exact name: {recipient_name} (ID: {recipient.get('id')})")
                    return {
                        "recipient_exists": True,
                        "matched_recipient_id": recipient.get("id")
                    }
            
            # Then try fuzzy match (with higher threshold for better accuracy)
            for recipient in user_recipients:
                recipient_name = recipient.get("name", "")
                if recipient_name:
                    recipient_name_normalized = " ".join(recipient_name.lower().strip().split())
                    # Use normalized names for fuzzy matching
                    if _fuzzy_match_name(person_name_normalized, recipient_name_normalized, threshold=0.85):
                        logger.info(f"Matched recipient by fuzzy name: {recipient_name} (ID: {recipient.get('id')})")
                        return {
                            "recipient_exists": True,
                            "matched_recipient_id": recipient.get("id"),
                            "ambiguous_recipients": None
                        }
        
        # Only match by relationship if name matching failed AND we have a relationship
        if person_relationship and not person_name:
            matching_by_relationship = [
                r for r in user_recipients
                if r.get("relationship", "").lower() == person_relationship.lower()
            ]
            
            if len(matching_by_relationship) == 1:
                # Only one person with this relationship - safe to match
                recipient = matching_by_relationship[0]
                logger.info(f"Matched recipient by unique relationship: {recipient.get('relationship')} - {recipient.get('name')} (ID: {recipient.get('id')})")
                return {
                    "recipient_exists": True,
                    "matched_recipient_id": recipient.get("id"),
                    "ambiguous_recipients": None
                }
            elif len(matching_by_relationship) > 1:
                # Multiple people with same relationship - mark as ambiguous
                # Return the list of matching recipients so we can ask for clarification
                logger.info(f"Ambiguous relationship match: {len(matching_by_relationship)} people have relationship '{person_relationship}'. Need name to disambiguate.")
                return {
                    "recipient_exists": True,  # At least one exists, but ambiguous
                    "matched_recipient_id": None,  # Can't match without name
                    "ambiguous_recipients": [  # List of possible matches
                        {
                            "id": r.get("id"),
                            "name": r.get("name"),
                            "relationship": r.get("relationship")
                        }
                        for r in matching_by_relationship
                    ]
                    }
        
        logger.info("No matching recipient found")
        return {"recipient_exists": False, "matched_recipient_id": None}
        
    except Exception as e:
        logger.error(f"Error in check_recipient_node: {e}", exc_info=True)
        return {"recipient_exists": False, "matched_recipient_id": None, "error": str(e)}


async def process_relationships_node(state: AgentState) -> Dict[str, Any]:
    """
    Process relationship information and create secondary contacts.
    Detects statements like "Ravi's wife is Archana" and creates:
    - Secondary contact (Archana) if doesn't exist
    - Relationship link between primary and secondary
    Returns: {"pending_actions": List[dict]} with create_secondary_contact actions
    """
    try:
        detected_person = state.get("detected_person")
        matched_recipient_id = state.get("matched_recipient_id")
        user_recipients = state.get("user_recipients", [])
        pending_actions = state.get("pending_actions", [])
        
        if not detected_person:
            return {"pending_actions": pending_actions}
        
        secondary_contacts = detected_person.get("secondary_contacts", [])
        if not secondary_contacts:
            return {"pending_actions": pending_actions}
        
        # Need a primary recipient to link relationships to
        primary_recipient_id = matched_recipient_id
        if not primary_recipient_id:
            # Try to find by name
            primary_name = detected_person.get("name")
            if primary_name:
                for recipient in user_recipients:
                    if recipient.get("name", "").lower() == primary_name.lower():
                        primary_recipient_id = recipient.get("id")
                        break
        
        if not primary_recipient_id:
            logger.warning(f"Cannot create relationships: no primary recipient found for {detected_person.get('name')}")
            return {"pending_actions": pending_actions}
        
        # Process each secondary contact
        for secondary in secondary_contacts:
            secondary_name = secondary.get("name")
            relationship_type = secondary.get("relationship_to_primary", "").lower()
            
            if not secondary_name:
                continue
            
            # Check if secondary contact already exists
            existing_secondary = None
            for recipient in user_recipients:
                if recipient.get("name", "").lower() == secondary_name.lower():
                    existing_secondary = recipient
                    break
            
            # Determine if relationship is bidirectional (spouse/partner relationships)
            is_bidirectional = relationship_type in ["wife", "husband", "spouse", "partner"]
            
            if existing_secondary:
                # Secondary contact exists, just create the relationship
                pending_actions.append({
                    "type": "create_relationship",
                    "from_recipient_id": primary_recipient_id,
                    "to_recipient_id": existing_secondary.get("id"),
                    "relationship_type": relationship_type,
                    "is_bidirectional": is_bidirectional
                })
            else:
                # Create new secondary contact and relationship
                pending_actions.append({
                    "type": "create_secondary_contact",
                    "primary_recipient_id": primary_recipient_id,
                    "secondary_contact": {
                        "name": secondary_name,
                        "relationship_type": relationship_type,
                        "is_core_contact": False,
                        "network_level": 2
                    },
                    "is_bidirectional": is_bidirectional
                })
        
        logger.info(f"Processed {len(secondary_contacts)} secondary contacts, created {len([a for a in pending_actions if a.get('type') in ['create_secondary_contact', 'create_relationship']])} relationship actions")
        
        return {"pending_actions": pending_actions}
        
    except Exception as e:
        logger.error(f"Error in process_relationships_node: {e}", exc_info=True)
        return {"pending_actions": state.get("pending_actions", [])}


async def generate_gifts_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate 5 personalized gift ideas using ChatOpenAI.
    Build context from recipient info.
    For anniversary gifts, considers both partners' interests.
    Returns: {"gift_ideas": [GiftIdea]}
    """
    try:
        detected_person = state.get("detected_person")
        matched_recipient_id = state.get("matched_recipient_id")
        user_recipients = state.get("user_recipients", [])
        messages = state.get("messages", [])
        
        # Check if this is an anniversary gift request
        is_anniversary = False
        if messages:
            last_message = messages[-1] if messages else None
            message_text = last_message.content if last_message and hasattr(last_message, 'content') else ""
            is_anniversary = "anniversary" in message_text.lower() or "wedding" in message_text.lower()
        
        # Get recipient info (either from detected_person or matched recipient)
        recipient_info = detected_person or {}
        partner_info = None
        
        if matched_recipient_id:
            # Use existing recipient data
            matched_recipient = next(
                (r for r in user_recipients if r.get("id") == matched_recipient_id),
                None
            )
            if matched_recipient:
                recipient_info = {
                    "name": matched_recipient.get("name"),
                    "relationship": matched_recipient.get("relationship"),
                    "interests": matched_recipient.get("interests", []),
                    "age_band": matched_recipient.get("age_band"),
                    "constraints": matched_recipient.get("constraints", [])
                }
                
                # For anniversary gifts, find partner
                if is_anniversary:
                    relationships = matched_recipient.get("relationships", [])
                    # Find spouse/partner relationship
                    partner_relationship = next(
                        (r for r in relationships if r.get("relationship_type") in ["wife", "husband", "spouse", "partner"]),
                        None
                    )
                    if partner_relationship:
                        partner_id = partner_relationship.get("to_recipient_id")
                        partner = next(
                            (r for r in user_recipients if r.get("id") == partner_id),
                            None
                        )
                        if partner:
                            partner_info = {
                                "name": partner.get("name"),
                                "interests": partner.get("interests", []),
                                "age_band": partner.get("age_band"),
                                "constraints": partner.get("constraints", [])
                }
        
        if not recipient_info.get("name") and not recipient_info.get("relationship"):
            return {"gift_ideas": [], "error": "Insufficient recipient information"}
        
        # Build context string
        context_parts = []
        if recipient_info.get("name"):
            context_parts.append(f"Name: {recipient_info['name']}")
        if recipient_info.get("relationship"):
            context_parts.append(f"Relationship: {recipient_info['relationship']}")
        if recipient_info.get("age_band"):
            context_parts.append(f"Age: {recipient_info['age_band']}")
        if recipient_info.get("interests"):
            context_parts.append(f"Interests: {', '.join(recipient_info['interests'])}")
        if recipient_info.get("constraints"):
            context_parts.append(f"Constraints: {', '.join(recipient_info['constraints'])}")
        
        # Add partner info for anniversary gifts
        if partner_info:
            context_parts.append(f"\nPartner Information (for anniversary gift):")
            context_parts.append(f"Partner Name: {partner_info.get('name')}")
            if partner_info.get("interests"):
                context_parts.append(f"Partner Interests: {', '.join(partner_info['interests'])}")
            if partner_info.get("age_band"):
                context_parts.append(f"Partner Age: {partner_info['age_band']}")
        
        context = "\n".join(context_parts)
        
        # Create prompt for gift generation
        system_prompt = """You are a gift recommendation expert. Generate 5 personalized, thoughtful gift ideas.
For each gift, provide:
- title: Clear, descriptive name
- description: 2-3 sentences explaining why it's a good gift
- price: Price or price range (e.g., "$50", "$20-30")
- category: Category (electronics, books, experiences, clothing, home, etc.)
- url: Product URL if you know a specific one, otherwise None

Make gifts thoughtful, personalized, and appropriate for the recipient.
Consider their interests, age, and relationship to the gift giver.
Include a mix of price ranges and categories."""
        
        if partner_info:
            system_prompt += "\n\nIMPORTANT: This is an anniversary gift. Consider BOTH partners' interests when generating gift ideas. Suggest gifts that both people can enjoy together, experiences they can share, or items that enhance their relationship."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Generate gift ideas for:\n{context}")
        ])
        
        # Get LLM with structured output
        llm = get_llm(temperature=0.7)
        structured_llm = llm.with_structured_output(GiftIdeasList)
        
        # Invoke LLM
        result = await structured_llm.ainvoke(prompt.format_messages(context=context))
        
        # Convert to list of dicts
        gift_ideas = [
            {
                "title": gift.title,
                "description": gift.description,
                "price": gift.price,
                "category": gift.category,
                "url": gift.url
            }
            for gift in result.gift_ideas
        ]
        
        logger.info(f"Generated {len(gift_ideas)} gift ideas")
        
        return {"gift_ideas": gift_ideas}
        
    except Exception as e:
        logger.error(f"Error in generate_gifts_node: {e}", exc_info=True)
        return {"gift_ideas": [], "error": str(e)}


async def compose_response_node(state: AgentState) -> Dict[str, Any]:
    """
    Craft final AI response based on intent and data.
    Handle gift search, add recipient, update info, casual chat.
    Returns: {
        "ai_response": str,
        "requires_confirmation": bool,
        "confirmation_prompt": str or None,
        "pending_actions": List[dict]
    }
    """
    try:
        current_intent = state.get("current_intent")
        detected_person = state.get("detected_person")
        recipient_exists = state.get("recipient_exists")
        matched_recipient_id = state.get("matched_recipient_id")
        ambiguous_recipients = state.get("ambiguous_recipients")
        gift_ideas = state.get("gift_ideas", [])
        messages = state.get("messages", [])
        user_recipients = state.get("user_recipients", [])
        
        # Get last user message for context
        last_message = messages[-1] if messages else None
        user_message = last_message.content if last_message and hasattr(last_message, 'content') else ""
        
        ai_response = ""
        requires_confirmation = False
        confirmation_prompt = None
        # Start with existing pending_actions from previous nodes (e.g., process_relationships_node)
        pending_actions = state.get("pending_actions", [])
        
        if current_intent == "gift_search":
            if gift_ideas:
                # Format gift ideas nicely
                gift_list = "\n".join([
                    f"{i+1}. **{gift['title']}** - {gift['price']}\n   {gift['description']}"
                    for i, gift in enumerate(gift_ideas)
                ])
                ai_response = f"Here are some personalized gift ideas:\n\n{gift_list}\n\nWould you like me to save these suggestions or look for more options?"
            else:
                # No gift ideas generated - check if we have recipient info
                recipient_name = None
                if matched_recipient_id:
                    matched_recipient = next(
                        (r for r in user_recipients if r.get("id") == matched_recipient_id),
                        None
                    )
                    if matched_recipient:
                        recipient_name = matched_recipient.get("name")
                
                if not recipient_name and detected_person:
                    recipient_name = detected_person.get("name")
                
                if recipient_name:
                    ai_response = f"I'd be happy to help you find the perfect gift for {recipient_name}! Could you tell me a bit more about them? For example, their interests, age, or relationship to you?"
                else:
                    ai_response = "I'd be happy to help you find the perfect gift! Could you tell me a bit more about the person? For example, their name, interests, age, or relationship to you?"
        
        elif current_intent == "add_recipient":
            # Check if we have enough information to add a recipient
            has_name = detected_person and detected_person.get("name")
            has_relationship = detected_person and detected_person.get("relationship")
            has_minimum_info = has_name or has_relationship
            
            user_recipients = state.get("user_recipients", [])
            
            logger.info(f"add_recipient: recipient_exists={recipient_exists}, has_name={has_name}, has_relationship={has_relationship}, detected_person={detected_person}")
            
            if not recipient_exists and has_minimum_info:
                # We have enough info to add
                person_name = detected_person.get("name") or detected_person.get("relationship", "this person")
                
                # Check if address information was provided
                street_address = detected_person.get("street_address")
                city = detected_person.get("city")
                has_address = street_address and city
                
                # Check if occasion information was provided
                occasion_name = detected_person.get("occasion_name")
                occasion_date = detected_person.get("occasion_date")
                
                requires_confirmation = True
                if occasion_name and occasion_date:
                    confirmation_prompt = f"Would you like me to add {person_name} to your network with their {occasion_name} ({occasion_date})?"
                    # Create recipient action (occasion will be added after recipient is created)
                    pending_actions.append({
                        "type": "create_recipient",
                        "data": detected_person,
                        "occasion_data": {
                            "name": occasion_name,
                            "occasion_type": occasion_name.lower(),
                            "date": occasion_date
                        }
                    })
                    ai_response = f"I'd like to add {person_name} to your network with their {occasion_name} ({occasion_date}). {confirmation_prompt}"
                    # Prompt for address if missing
                    if not has_address:
                        ai_response += f" Also, I'd like to add {person_name}'s address for shipping purposes. Could you provide their street address, city, state, and postal code?"
                else:
                    confirmation_prompt = f"Would you like me to add {person_name} to your network? I'll remember their preferences for future gift suggestions."
                    pending_actions.append({
                        "type": "create_recipient",
                        "data": detected_person
                    })
                    ai_response = f"I'd like to add {person_name} to your network so I can provide better gift suggestions. {confirmation_prompt}"
                    # Prompt for address if missing
                    if not has_address:
                        ai_response += f" Also, I'd like to add {person_name}'s address for shipping purposes. Could you provide their street address, city, state, and postal code?"
            elif recipient_exists:
                # Person exists, check if they're providing new information to update
                # Get person name first - try from detected_person, then from matched recipient
                person_name = None
                if detected_person:
                    person_name = detected_person.get("name")
                
                if not person_name and matched_recipient_id:
                    matched_recipient = next(
                        (r for r in user_recipients if r.get("id") == matched_recipient_id),
                        None
                    )
                    if matched_recipient:
                        person_name = matched_recipient.get("name")
                
                if not person_name:
                    person_name = "this person"
                
                # Extract data from detected_person if available
                occasion_name = None
                occasion_date = None
                interests = []
                notes = None
                age_band = None
                secondary_contacts = []
                
                if detected_person:
                    occasion_name = detected_person.get("occasion_name")
                    occasion_date = detected_person.get("occasion_date")
                    interests = detected_person.get("interests", [])
                    notes = detected_person.get("notes")
                    age_band = detected_person.get("age_band")
                    secondary_contacts = detected_person.get("secondary_contacts", [])
                
                # If notes weren't extracted but message contains additional info, use the message as notes
                if not notes and detected_person and user_message:
                    # Check if message has info beyond just interests (family details, etc.)
                    if interests:
                        # If message is longer than just interests, it might contain notes
                        interests_text = ", ".join(interests).lower()
                        if user_message.lower() != interests_text and len(user_message) > len(interests_text) + 10:
                            notes = user_message
                    else:
                        # No interests extracted but message exists - likely contains notes
                        notes = user_message
                
                # Check if address information was provided
                street_address = detected_person.get("street_address") if detected_person else None
                city = detected_person.get("city") if detected_person else None
                has_address = street_address and city
                
                # Check if secondary contacts are being added (relationships)
                has_secondary_contacts = len(secondary_contacts) > 0
                has_new_info = (occasion_name and occasion_date) or interests or notes or age_band or has_secondary_contacts or (street_address or city)
                
                if has_new_info and matched_recipient_id:
                    # They're providing new info for existing person - treat as update_info
                    matched_recipient = next(
                        (r for r in user_recipients if r.get("id") == matched_recipient_id),
                        None
                    )
                    if matched_recipient:
                        person_name = matched_recipient.get("name", person_name)
                    
                    # Build update data
                    update_data = {}
                    if interests:
                        update_data["interests"] = interests
                    if notes:
                        update_data["notes"] = notes
                    if age_band:
                        update_data["age_band"] = age_band
                    if street_address:
                        update_data["street_address"] = street_address
                    if city:
                        update_data["city"] = city
                    if detected_person.get("state_province"):
                        update_data["state_province"] = detected_person.get("state_province")
                    if detected_person.get("postal_code"):
                        update_data["postal_code"] = detected_person.get("postal_code")
                    if detected_person.get("country"):
                        update_data["country"] = detected_person.get("country")
                    
                    # Create actions
                    if occasion_name and occasion_date:
                        pending_actions.append({
                            "type": "create_occasion",
                            "recipient_id": matched_recipient_id,
                            "occasion_data": {
                                "name": occasion_name,
                                "occasion_type": occasion_name.lower(),
                                "date": occasion_date
                            }
                        })
                    
                    if update_data:
                        pending_actions.append({
                            "type": "update_recipient",
                            "recipient_id": matched_recipient_id,
                            "data": update_data
                        })
                    
                    # Build confirmation message
                    updates_list = []
                    if occasion_name and occasion_date:
                        updates_list.append(f"add {occasion_name} ({occasion_date})")
                    if age_band:
                        updates_list.append(f"update age to {age_band}")
                    if interests:
                        updates_list.append(f"update interests to {', '.join(interests)}")
                    if notes:
                        updates_list.append("update notes")
                    if street_address or city:
                        address_parts = []
                        if street_address:
                            address_parts.append(street_address)
                        if city:
                            address_parts.append(city)
                        if detected_person.get("state_province"):
                            address_parts.append(detected_person.get("state_province"))
                        if detected_person.get("postal_code"):
                            address_parts.append(detected_person.get("postal_code"))
                        updates_list.append(f"update address to {', '.join(address_parts)}")
                    if has_secondary_contacts:
                        # Add relationship info to confirmation
                        relationship_descriptions = []
                        for sec in secondary_contacts:
                            rel_type = sec.get("relationship_to_primary", "")
                            sec_name = sec.get("name", "")
                            if rel_type and sec_name:
                                relationship_descriptions.append(f"add {sec_name} as {person_name}'s {rel_type}")
                        if relationship_descriptions:
                            updates_list.append(", ".join(relationship_descriptions))
                    
                    requires_confirmation = True
                    confirmation_prompt = f"Would you like me to {', '.join(updates_list)} for {person_name}?"
                    ai_response = f"I can {', '.join(updates_list)} for {person_name}. {confirmation_prompt}"
                else:
                    ai_response = "This person is already in your network! I can help you find gift ideas for them."
            else:
                # Missing information - ask for what's needed
                missing_info = []
                if not has_name:
                    missing_info.append("name")
                if not has_relationship:
                    missing_info.append("relationship")
                ai_response = f"I'd be happy to add someone to your network! Could you tell me their {', '.join(missing_info)}?"
        
        elif current_intent == "update_info":
            # Check for ambiguous recipients first
            if ambiguous_recipients and len(ambiguous_recipients) > 1:
                names_list = ", ".join([r.get("name", "Unknown") for r in ambiguous_recipients])
                relationship = detected_person.get("relationship", "person") if detected_person else "person"
                ai_response = f"I see you have multiple {relationship}s in your network: {names_list}. Which one would you like to update? Please specify the name."
                return {
                    "ai_response": ai_response,
                    "requires_confirmation": False,
                    "confirmation_prompt": None,
                    "pending_actions": pending_actions
                }
            
            if recipient_exists and matched_recipient_id and detected_person:
                # Get the actual matched recipient name to use in the response
                user_recipients = state.get("user_recipients", [])
                matched_recipient = next(
                    (r for r in user_recipients if r.get("id") == matched_recipient_id),
                    None
                )
                
                # Use the matched recipient's name (from database) for accuracy
                if matched_recipient:
                    person_name = matched_recipient.get("name", detected_person.get("name", "this person"))
                else:
                    person_name = detected_person.get("name", "this person")
                
                # Check if occasion information was provided
                occasion_name = detected_person.get("occasion_name")
                occasion_date = detected_person.get("occasion_date")
                age_band = detected_person.get("age_band")
                interests = detected_person.get("interests", [])
                notes = detected_person.get("notes")
                secondary_contacts = detected_person.get("secondary_contacts", [])
                has_secondary_contacts = len(secondary_contacts) > 0
                # Check address fields
                street_address = detected_person.get("street_address")
                city = detected_person.get("city")
                state_province = detected_person.get("state_province")
                postal_code = detected_person.get("postal_code")
                country = detected_person.get("country")
                
                # Build update data
                update_data = {}
                if age_band:
                    update_data["age_band"] = age_band
                if interests:
                    update_data["interests"] = interests
                if notes:
                    update_data["notes"] = notes
                if street_address:
                    update_data["street_address"] = street_address
                if city:
                    update_data["city"] = city
                if state_province:
                    update_data["state_province"] = state_province
                if postal_code:
                    update_data["postal_code"] = postal_code
                if country:
                    update_data["country"] = country
                
                # Build updates list for confirmation message
                updates_list = []
                
                requires_confirmation = True
                if occasion_name and occasion_date:
                    # Create occasion action
                    updates_list.append(f"add {occasion_name} ({occasion_date})")
                    pending_actions.append({
                        "type": "create_occasion",
                        "recipient_id": matched_recipient_id,
                        "occasion_data": {
                            "name": occasion_name,
                            "occasion_type": occasion_name.lower(),
                            "date": occasion_date
                        }
                    })
                
                if age_band:
                    updates_list.append(f"update age to {age_band}")
                if interests:
                    updates_list.append(f"update interests to {', '.join(interests)}")
                if notes:
                    updates_list.append("update notes")
                if street_address or city:
                    address_parts = []
                    if street_address:
                        address_parts.append(street_address)
                    if city:
                        address_parts.append(city)
                    if state_province:
                        address_parts.append(state_province)
                    if postal_code:
                        address_parts.append(postal_code)
                    updates_list.append(f"update address to {', '.join(address_parts)}")
                
                if has_secondary_contacts:
                    # Add relationship info to confirmation
                    relationship_descriptions = []
                    for sec in secondary_contacts:
                        rel_type = sec.get("relationship_to_primary", "")
                        sec_name = sec.get("name", "")
                        if rel_type and sec_name:
                            relationship_descriptions.append(f"add {sec_name} as {person_name}'s {rel_type}")
                    if relationship_descriptions:
                        updates_list.extend(relationship_descriptions)
                
                if updates_list:
                    confirmation_prompt = f"Would you like me to {', '.join(updates_list)} for {person_name}?"
                    ai_response = f"I can {', '.join(updates_list)} for {person_name}. {confirmation_prompt}"
                    
                    # Add update_recipient action if there's data to update
                    if update_data:
                        pending_actions.append({
                            "type": "update_recipient",
                            "recipient_id": matched_recipient_id,
                            "data": update_data
                        })
                else:
                    # Regular update (no specific updates detected, use full detected_person)
                    requires_confirmation = True
                    confirmation_prompt = f"Would you like me to update the information for {person_name}?"
                    pending_actions.append({
                        "type": "update_recipient",
                        "recipient_id": matched_recipient_id,
                        "data": detected_person
                    })
                    ai_response = f"I can update the information for {person_name}. {confirmation_prompt}"
            else:
                # Recipient not found, but check if we have occasion info - might be a new person
                occasion_name = detected_person.get("occasion_name") if detected_person else None
                occasion_date = detected_person.get("occasion_date") if detected_person else None
                person_name = detected_person.get("name") if detected_person else None
                
                if occasion_name and occasion_date and person_name:
                    # We have occasion info but recipient not found - treat as add_recipient
                    # This handles cases like "Manasa s birthday is nov 30" where name extraction might be imperfect
                    requires_confirmation = True
                    confirmation_prompt = f"Would you like me to add {person_name} to your network with their {occasion_name} ({occasion_date})?"
                    pending_actions.append({
                        "type": "create_recipient",
                        "data": detected_person,
                        "occasion_data": {
                            "name": occasion_name,
                            "occasion_type": occasion_name.lower(),
                            "date": occasion_date
                        }
                    })
                    ai_response = f"I'd like to add {person_name} to your network with their {occasion_name} ({occasion_date}). {confirmation_prompt}"
                else:
                    ai_response = "I'd be happy to update information! Could you tell me who you'd like to update and what information has changed?"
        
        elif current_intent == "casual_chat":
            # Check for ambiguous recipients first (e.g., "when is my sister's birthday?")
            if ambiguous_recipients and len(ambiguous_recipients) > 1:
                names_list = ", ".join([r.get("name", "Unknown") for r in ambiguous_recipients])
                relationship = detected_person.get("relationship", "person") if detected_person else "person"
                ai_response = f"I see you have multiple {relationship}s in your network: {names_list}. Which one are you asking about? Please specify the name."
                return {
                    "ai_response": ai_response,
                    "requires_confirmation": False,
                    "confirmation_prompt": None,
                    "pending_actions": []
                }
            
            # Use LLM for natural conversation with access to user's data
            user_recipients = state.get("user_recipients", [])
            user_occasions = state.get("user_occasions", [])
            
            # Format recipients for context
            recipients_context = ""
            if user_recipients:
                recipients_list = []
                for r in user_recipients:
                    recipient_str = f"- {r.get('name', 'Unknown')}"
                    if r.get('relationship'):
                        recipient_str += f" ({r.get('relationship')})"
                    if r.get('interests'):
                        recipient_str += f" - Interests: {', '.join(r.get('interests', []))}"
                    if r.get('notes'):
                        recipient_str += f" - Notes: {r.get('notes')}"
                    # Include relationships (secondary contacts)
                    relationships = r.get('relationships', [])
                    if relationships:
                        relationship_descriptions = []
                        for rel in relationships:
                            # Find the name of the related recipient
                            related_recipient_id = rel.get('to_recipient_id')
                            related_name = "Unknown"
                            if related_recipient_id:
                                related_recipient = next(
                                    (rec for rec in user_recipients if rec.get('id') == related_recipient_id),
                                    None
                                )
                                if related_recipient:
                                    related_name = related_recipient.get('name', 'Unknown')
                            rel_type = rel.get('relationship_type', '')
                            relationship_descriptions.append(f"{related_name} ({rel_type})")
                        if relationship_descriptions:
                            recipient_str += f" - Relationships: {', '.join(relationship_descriptions)}"
                    recipients_list.append(recipient_str)
                recipients_context = "\n".join(recipients_list)
            
            # Format occasions for context (grouped by recipient)
            occasions_context = ""
            if user_occasions:
                occasions_list = []
                for o in user_occasions:
                    # Find recipient name
                    recipient_id = o.get('recipient_id')
                    recipient_name = "Unknown"
                    if recipient_id:
                        recipient = next((r for r in user_recipients if r.get('id') == recipient_id), None)
                        if recipient:
                            recipient_name = recipient.get('name', 'Unknown')
                    
                    occasion_str = f"- {recipient_name}'s {o.get('name', 'Occasion')}"
                    if o.get('date'):
                        occasion_str += f" is on {o.get('date')}"
                    occasions_list.append(occasion_str)
                occasions_context = "\n".join(occasions_list)
            
            # Build system prompt with user data
            system_prompt = """You are My3, a friendly and helpful AI gift concierge assistant.
You help people remember important people in their lives and find perfect gifts.
Be warm, conversational, and helpful. Keep responses concise (2-3 sentences).

You have access to the user's network of important people and their occasions. Use this information to answer questions accurately.
IMPORTANT: 
- When answering questions about family members, relationships, or personal details, check the "Notes" field for each person - it contains additional information like family member names, personal details, and other context.
- When answering questions about relationships (e.g., "who is X's wife?"), check the "Relationships" field for each person - it shows their connections to other people in the network (e.g., "Relationships: Shravya (wife)" means this person's wife is Shravya)."""
            
            if recipients_context:
                system_prompt += f"\n\nPeople in the user's network:\n{recipients_context}"
            
            if occasions_context:
                system_prompt += f"\n\nOccasions:\n{occasions_context}"
            else:
                system_prompt += "\n\nOccasions: None stored yet."
            
            system_prompt += "\n\nWhen answering questions about people or occasions, use the information above. Be specific and accurate."
            system_prompt += "\n- CRITICAL: If the user asks 'Who is [name]?' or 'What do you know about [name]?', you MUST look up that person in the 'People in the user's network' list above. Find the person by name (case-insensitive) and provide a clear summary including: their relationship to the user, interests, age (if available), notes, relationships to other people, and any upcoming occasions."
            system_prompt += "\n- Example: If user asks 'Who is Ritika?', find 'Ritika' in the network list and respond with something like 'Ritika is your [relationship]. [Her interests are...] [She is...] [Her birthday/occasions are...]'"
            system_prompt += "\n- If the user asks about a birthday or occasion, check the occasions list above and provide the exact date if available."
            system_prompt += "\n- If the person is not found in the network list above, clearly state that you don't have information about that person yet, but you can help them add it."
            system_prompt += "\n- If you detect duplicate entries (same name and relationship), inform the user and ask if they want to remove the duplicates. When they confirm (say 'yes'), you should create delete_recipient actions for the duplicate entries (keep the one with the most information or the most recent one)."
            
            # Check for duplicates before generating response
            duplicates_found = []
            try:
                if user_recipients:
                    from collections import defaultdict
                    name_relationship_map = defaultdict(list)
                    for r in user_recipients:
                        key = (r.get('name', '').lower().strip(), r.get('relationship', '').lower().strip() if r.get('relationship') else None)
                        name_relationship_map[key].append(r)
                    
                    for key, recipients in name_relationship_map.items():
                        if len(recipients) > 1:
                            duplicates_found.append({
                                'name': key[0],
                                'relationship': key[1],
                                'recipients': recipients
                            })
            except Exception as e:
                logger.warning(f"Error detecting duplicates: {e}")
                duplicates_found = []
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{message}")
            ])
            
            llm = get_llm(temperature=0.7)
            response = await llm.ainvoke(prompt.format_messages(message=user_message))
            ai_response = response.content if hasattr(response, 'content') else str(response)
        
            # Check if previous AI message mentioned duplicates
            prev_ai_mentioned_duplicates = False
            try:
                if len(messages) > 1:
                    # Look for previous AI messages (skip the current user message)
                    for msg in reversed(messages[:-1]):
                        # Check if it's an AI message
                        if isinstance(msg, AIMessage):
                            prev_content = msg.content if hasattr(msg, 'content') else str(msg)
                            if "duplicate" in prev_content.lower() or "duplication" in prev_content.lower():
                                prev_ai_mentioned_duplicates = True
                                break
            except Exception as e:
                logger.warning(f"Error checking previous messages for duplicates: {e}")
                prev_ai_mentioned_duplicates = False
            
            # If user confirms duplicate removal and we found duplicates, create delete actions
            try:
                user_message_lower = user_message.lower()
                is_confirmation = any(word in user_message_lower for word in ["yes", "confirm", "correct", "remove", "help", "please"])
                
                if duplicates_found and prev_ai_mentioned_duplicates and is_confirmation:
                    # User confirmed duplicate removal - create delete actions
                    # Keep the one with most info, delete the rest
                    total_to_delete = 0
                    for dup_group in duplicates_found:
                        recipients = dup_group.get('recipients', [])
                        if len(recipients) > 1:
                            # Sort by amount of info (most complete first)
                            # Handle created_at which might be a string, datetime, or None
                            def sort_key(r):
                                created_at = r.get('created_at') or ''
                                # Convert datetime to string if needed for comparison
                                if created_at and hasattr(created_at, 'isoformat'):
                                    created_at = created_at.isoformat()
                                elif created_at:
                                    created_at = str(created_at)
                                else:
                                    created_at = ''
                                return (
                                    len(r.get('interests', []) or []),
                                    len(r.get('notes', '') or ''),
                                    len(r.get('relationships', []) or []),
                                    created_at
                                )
                            recipients_sorted = sorted(recipients, key=sort_key, reverse=True)
                            # Keep the first (most complete), delete the rest
                            to_keep = recipients_sorted[0]
                            to_delete = recipients_sorted[1:]
                            
                            for recipient_to_delete in to_delete:
                                recipient_id = recipient_to_delete.get('id')
                                if recipient_id:
                                    pending_actions.append({
                                        "type": "delete_recipient",
                                        "recipient_id": recipient_id
                                    })
                                    total_to_delete += 1
                    
                    if total_to_delete > 0:
                        requires_confirmation = True
                        confirmation_prompt = f"Would you like me to remove {total_to_delete} duplicate entr{'y' if total_to_delete == 1 else 'ies'}?"
                        ai_response = f"I'll remove {total_to_delete} duplicate entr{'y' if total_to_delete == 1 else 'ies'}, keeping the most complete ones. {confirmation_prompt}"
            except Exception as e:
                logger.warning(f"Error processing duplicate removal confirmation: {e}")
                # Continue with normal response if duplicate removal fails
        
        elif current_intent == "unclear" or current_intent is None:
            # If intent is unclear or None, try to provide a helpful response based on the message
            logger.warning(f"[WARNING] Intent is unclear or None. User message: '{user_message}'. Attempting fallback response.")
            
            # Check if there was an error that indicates API issues
            error = state.get("error", "")
            if error and ("insufficient_quota" in error.lower() or "quota" in error.lower() or "429" in error):
                ai_response = "I apologize, but I'm currently unable to process requests because the OpenAI API quota has been exhausted. Please add credits to your OpenAI account at https://platform.openai.com/account/billing and try again."
                logger.error("[CRITICAL] Returning quota exhaustion message to user")
                return {
                    "ai_response": ai_response,
                    "requires_confirmation": False,
                    "confirmation_prompt": None,
                    "pending_actions": [],
                    "messages": [AIMessage(content=ai_response)],
                    "error": error
                }
            
            user_message_lower = user_message.lower() if user_message else ""
            
            # Check if it's a question about a person (should have been casual_chat)
            if "who is" in user_message_lower or "what do you know about" in user_message_lower:
                # Try to extract name and look it up
                # This is a fallback for when intent classification fails
                # Actually, let's try to handle it as casual_chat even though intent is unclear
                logger.info("⚠️ Detected 'who is' question but intent is unclear. Handling as casual_chat.")
                # Force it to casual_chat by setting the intent and falling through
                # We'll handle it in the casual_chat section below
                # For now, provide a helpful response that tries to look up the person
                # Extract potential name from message
                name_parts = user_message_lower.replace("who is", "").replace("what do you know about", "").strip().split()
                potential_name = name_parts[0] if name_parts else None
                
                if potential_name:
                    # Try to find the person in the network
                    matched_recipient = None
                    for r in user_recipients:
                        if r.get('name', '').lower() == potential_name:
                            matched_recipient = r
                            break
                    
                    if matched_recipient:
                        # Build a response with their info
                        name = matched_recipient.get('name', 'Unknown')
                        relationship = matched_recipient.get('relationship', '')
                        interests = matched_recipient.get('interests', [])
                        age_band = matched_recipient.get('age_band', '')
                        notes = matched_recipient.get('notes', '')
                        
                        response_parts = [f"{name}"]
                        if relationship:
                            response_parts.append(f"is your {relationship}")
                        if interests:
                            response_parts.append(f"and likes {', '.join(interests)}")
                        if age_band:
                            response_parts.append(f"({age_band})")
                        if notes:
                            response_parts.append(f". Additional info: {notes}")
                        
                        ai_response = " ".join(response_parts) + "."
                    else:
                        ai_response = f"I don't have information about {potential_name} in your network yet. Would you like me to add them?"
                else:
                    ai_response = "I'd be happy to help! Could you tell me who you're asking about?"
            # Check if it's a gift search (should have been caught by fallback)
            elif "find" in user_message_lower and ("gift" in user_message_lower or "gifts" in user_message_lower):
                logger.warning("⚠️ Detected 'find gift' pattern but intent is unclear. This should have been caught by fallback.")
                ai_response = "I'd be happy to help you find gifts! Could you tell me who you're looking for gifts for?"
            else:
                ai_response = "I'm here to help you with gift ideas and managing your important relationships! What would you like to do? You can ask me to find gifts, add someone to your network, or update information about someone."
        
        logger.info(f"Composed response for intent: {current_intent}")
        
        return {
            "ai_response": ai_response,
            "requires_confirmation": requires_confirmation,
            "confirmation_prompt": confirmation_prompt,
            "pending_actions": pending_actions,
            "messages": [AIMessage(content=ai_response)]
        }
        
    except Exception as e:
        logger.error(f"Error in compose_response_node: {e}", exc_info=True)
        error_msg = "I apologize, but I encountered an error. Please try again."
        return {
            "ai_response": error_msg,
            "requires_confirmation": False,
            "confirmation_prompt": None,
            "pending_actions": [],
            "messages": [AIMessage(content=error_msg)],
            "error": str(e)
        }


async def execute_actions_node(state: AgentState) -> Dict[str, Any]:
    """
    Execute database operations (create recipient, update, etc.).
    Returns: {"pending_actions": []}
    
    Note: This node prepares actions but doesn't execute them directly.
    The chat route will execute actions after confirmation.
    """
    try:
        pending_actions = state.get("pending_actions", [])
        
        if not pending_actions:
            return {"pending_actions": []}
        
        # Actions are validated and ready to execute
        # They will be executed by the chat route after confirmation
        logger.info(f"Validated {len(pending_actions)} pending actions")
        
        return {"pending_actions": pending_actions}
        
    except Exception as e:
        logger.error(f"Error in execute_actions_node: {e}", exc_info=True)
        return {"pending_actions": [], "error": str(e)}
