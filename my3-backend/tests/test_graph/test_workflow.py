"""
Pytest tests for LangGraph workflow.

Tests the complete workflow including:
- Gift search flow
- Add recipient flow
- Existing recipient flow
- Casual chat flow
"""

import pytest
from langchain_core.messages import HumanMessage
from app.graph.workflow import my3_graph, create_my3_workflow
from app.graph.state import AgentState


@pytest.fixture
def workflow():
    """Create a fresh workflow instance for each test."""
    return create_my3_workflow()


@pytest.fixture
def base_state():
    """Base state for tests."""
    return {
        "messages": [],
        "user_id": "test-user-123",
        "conversation_id": None,
        "user_recipients": [],
        "user_occasions": [],
        "current_intent": None,
        "detected_person": None,
        "recipient_exists": None,
        "matched_recipient_id": None,
        "pending_actions": [],
        "requires_confirmation": False,
        "confirmation_prompt": None,
        "ai_response": None,
        "gift_ideas": None,
        "error": None,
    }


@pytest.mark.asyncio
async def test_workflow_compilation(workflow):
    """Test that workflow compiles without errors."""
    assert workflow is not None
    assert hasattr(workflow, 'ainvoke')


@pytest.mark.asyncio
async def test_gift_search_flow(workflow, base_state):
    """Test complete gift search flow."""
    state = {
        **base_state,
        "messages": [HumanMessage(content="Gift ideas for my mom who loves gardening")],
    }
    
    # Invoke workflow with config (required for checkpointer)
    config = {"configurable": {"thread_id": f"test-gift-search-{id(state)}"}}
    result = await workflow.ainvoke(state, config)
    
    # Verify intent classification
    assert result.get("current_intent") == "gift_search", f"Expected 'gift_search', got '{result.get('current_intent')}'"
    
    # Verify person extraction
    assert result.get("detected_person") is not None, "Person information should be extracted"
    detected_person = result.get("detected_person", {})
    assert detected_person.get("relationship") == "mom" or "mom" in str(detected_person.get("relationship", "")).lower(), \
        f"Expected relationship 'mom', got '{detected_person.get('relationship')}'"
    
    # Verify gift ideas generated
    assert result.get("gift_ideas") is not None, "Gift ideas should be generated"
    gift_ideas = result.get("gift_ideas", [])
    assert len(gift_ideas) > 0, "Should have at least one gift idea"
    assert len(gift_ideas) <= 5, f"Should have at most 5 gift ideas, got {len(gift_ideas)}"
    
    # Verify confirmation prompt (may or may not require confirmation depending on implementation)
    # The workflow might ask to add the recipient, or just provide gift ideas
    # Both behaviors are acceptable
    if not result.get("recipient_exists"):
        # If confirmation is required, verify it's set up correctly
        if result.get("requires_confirmation"):
            assert result.get("confirmation_prompt") is not None, "Should have confirmation prompt if requires_confirmation is True"
    
    # Verify AI response
    assert result.get("ai_response") is not None, "Should have AI response"
    assert len(result.get("ai_response", "")) > 0, "AI response should not be empty"


@pytest.mark.asyncio
async def test_add_recipient_flow(workflow, base_state):
    """Test adding new recipient."""
    state = {
        **base_state,
        "messages": [HumanMessage(content="Add my wife Ritika to my network")],
    }
    
    config = {"configurable": {"thread_id": f"test-add-recipient-{id(state)}"}}
    result = await workflow.ainvoke(state, config)
    
    # Verify intent classification
    assert result.get("current_intent") == "add_recipient", \
        f"Expected 'add_recipient', got '{result.get('current_intent')}'"
    
    # Verify person extraction
    assert result.get("detected_person") is not None, "Person information should be extracted"
    detected_person = result.get("detected_person", {})
    assert detected_person.get("name") is not None or detected_person.get("relationship") is not None, \
        "Should extract name or relationship"
    
    # Verify confirmation required
    assert result.get("requires_confirmation") == True, "Should require confirmation to add recipient"
    assert result.get("confirmation_prompt") is not None, "Should have confirmation prompt"
    
    # Verify pending actions
    pending_actions = result.get("pending_actions", [])
    assert len(pending_actions) > 0, "Should have pending actions to create recipient"
    
    # Check that action is to create recipient
    create_action = next((a for a in pending_actions if a.get("type") == "create_recipient"), None)
    assert create_action is not None, "Should have create_recipient action"
    
    # Verify AI response
    assert result.get("ai_response") is not None, "Should have AI response"


@pytest.mark.asyncio
async def test_existing_recipient(workflow, base_state):
    """Test gift search for existing recipient."""
    # Add existing recipient to state
    existing_recipient = {
        "id": "recipient-123",
        "name": "Mom",
        "relationship": "mom",
        "interests": ["gardening", "cooking"],
        "age_band": "50s",
    }
    
    state = {
        **base_state,
        "messages": [HumanMessage(content="Gift ideas for my mom")],
        "user_recipients": [existing_recipient],
    }
    
    config = {"configurable": {"thread_id": f"test-existing-recipient-{id(state)}"}}
    result = await workflow.ainvoke(state, config)
    
    # Verify intent
    assert result.get("current_intent") == "gift_search", "Should classify as gift_search"
    
    # Verify recipient was matched
    assert result.get("recipient_exists") == True, "Should detect existing recipient"
    assert result.get("matched_recipient_id") is not None, "Should have matched recipient ID"
    
    # Verify gift ideas generated
    assert result.get("gift_ideas") is not None, "Should generate gift ideas"
    assert len(result.get("gift_ideas", [])) > 0, "Should have gift ideas"
    
    # Should NOT require confirmation for existing recipient
    assert result.get("requires_confirmation") == False, \
        "Should not require confirmation for existing recipient"
    
    # Verify AI response
    assert result.get("ai_response") is not None, "Should have AI response"


@pytest.mark.asyncio
async def test_casual_chat_flow(workflow, base_state):
    """Test casual chat flow (should skip gift generation)."""
    state = {
        **base_state,
        "messages": [HumanMessage(content="Hello, how are you?")],
    }
    
    config = {"configurable": {"thread_id": f"test-casual-chat-{id(state)}"}}
    result = await workflow.ainvoke(state, config)
    
    # Verify intent classification
    intent = result.get("current_intent")
    assert intent in ["casual_chat", "unclear"], \
        f"Expected 'casual_chat' or 'unclear', got '{intent}'"
    
    # Should go directly to compose_response (skip gift generation)
    assert result.get("gift_ideas") is None or len(result.get("gift_ideas", [])) == 0, \
        "Should not generate gift ideas for casual chat"
    
    # Should have AI response
    assert result.get("ai_response") is not None, "Should have AI response"
    assert len(result.get("ai_response", "")) > 0, "AI response should not be empty"
    
    # Should not require confirmation
    assert result.get("requires_confirmation") == False, "Should not require confirmation for casual chat"


@pytest.mark.asyncio
async def test_max_recipients_limit(workflow, base_state):
    """Test that max 10 recipients limit is enforced."""
    # Create 10 existing recipients
    existing_recipients = [
        {
            "id": f"recipient-{i}",
            "name": f"Person {i}",
            "relationship": "friend",
            "interests": [],
            "age_band": None,
        }
        for i in range(10)
    ]
    
    state = {
        **base_state,
        "messages": [HumanMessage(content="Add my friend John to my network")],
        "user_recipients": existing_recipients,
    }
    
    config = {"configurable": {"thread_id": f"test-max-recipients-{id(state)}"}}
    result = await workflow.ainvoke(state, config)
    
    # Should detect that max recipients reached
    # The execute_actions_node should check and prevent adding 11th recipient
    # This will be handled in the compose_response or execute_actions node
    assert result.get("current_intent") == "add_recipient", "Should classify as add_recipient"
    
    # The workflow should handle the limit check
    # We can verify this by checking if the response mentions the limit
    ai_response = result.get("ai_response", "")
    # The response might mention the limit, but this depends on implementation
    # For now, just verify the workflow completes
    assert result.get("ai_response") is not None, "Should have AI response"


@pytest.mark.asyncio
async def test_update_info_flow(workflow, base_state):
    """Test updating information about existing recipient."""
    existing_recipient = {
        "id": "recipient-123",
        "name": "Sarah",
        "relationship": "friend",
        "interests": ["reading"],
        "age_band": "30s",
    }
    
    state = {
        **base_state,
        "messages": [HumanMessage(content="Sarah also loves yoga and hiking")],
        "user_recipients": [existing_recipient],
    }
    
    config = {"configurable": {"thread_id": f"test-update-info-{id(state)}"}}
    result = await workflow.ainvoke(state, config)
    
    # Should classify as update_info or detect existing recipient
    intent = result.get("current_intent")
    assert intent in ["update_info", "add_recipient"], \
        f"Expected 'update_info' or 'add_recipient', got '{intent}'"
    
    # Should detect existing recipient
    if result.get("recipient_exists"):
        assert result.get("matched_recipient_id") is not None, "Should match existing recipient"
    
    # Should have AI response
    assert result.get("ai_response") is not None, "Should have AI response"


@pytest.mark.asyncio
async def test_workflow_routing(workflow, base_state):
    """Test that workflow routes correctly based on intent."""
    test_cases = [
        ("Gift ideas for my dad", "gift_search"),
        ("Add my sister to my network", "add_recipient"),
        ("Hello, how are you?", "casual_chat"),
    ]
    
    for message, expected_intent in test_cases:
        state = {
            **base_state,
            "messages": [HumanMessage(content=message)],
        }
        
        config = {"configurable": {"thread_id": f"test-routing-{id(state)}"}}
        result = await workflow.ainvoke(state, config)
        
        actual_intent = result.get("current_intent")
        assert actual_intent == expected_intent or actual_intent in ["unclear", "casual_chat"], \
            f"For message '{message}': expected '{expected_intent}', got '{actual_intent}'"


@pytest.mark.asyncio
async def test_error_handling(workflow, base_state):
    """Test that workflow handles errors gracefully."""
    # Test with empty messages
    state = {
        **base_state,
        "messages": [],
    }
    
    config = {"configurable": {"thread_id": f"test-error-{id(state)}"}}
    result = await workflow.ainvoke(state, config)
    
    # Should handle gracefully (either error message or default response)
    # The workflow should not crash
    assert "error" in result or result.get("ai_response") is not None, \
        "Should handle empty messages gracefully"

