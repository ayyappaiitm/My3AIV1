# Testing Task 2.3: LangGraph Workflow

## Quick Test Methods

### Method 1: Run Test Script (Recommended)

```bash
cd my3-backend
python test_workflow_2.3.py
```

This script will:
- ✅ Test workflow compilation
- ✅ Test workflow structure
- ✅ Test gift search flow (requires OpenAI API key)
- ✅ Test casual chat flow (requires OpenAI API key)
- ✅ Test add recipient flow (requires OpenAI API key)

**Note:** The script will ask if you want to run API-dependent tests (which require OpenAI API key).

### Method 2: Test via API Endpoint

1. **Start the backend:**
   ```bash
   cd my3-backend
   # Activate virtual environment
   . venv/Scripts/activate  # Windows
   # or
   source venv/bin/activate  # Mac/Linux
   
   # Start server
   uvicorn app.main:app --reload
   ```

2. **Test the chat endpoint:**
   
   **Option A: Using curl**
   ```bash
   # First, register/login to get a token
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "testpass123", "name": "Test User"}'
   
   # Get token from response, then:
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"message": "Gift ideas for my mom who loves gardening"}'
   ```
   
   **Option B: Using Python requests**
   ```python
   import requests
   
   # Register
   response = requests.post("http://localhost:8000/api/auth/register", json={
       "email": "test@example.com",
       "password": "testpass123",
       "name": "Test User"
   })
   token = response.json()["access_token"]
   
   # Test chat
   chat_response = requests.post(
       "http://localhost:8000/api/chat",
       headers={"Authorization": f"Bearer {token}"},
       json={"message": "Gift ideas for my mom who loves gardening"}
   )
   print(chat_response.json())
   ```
   
   **Option C: Using FastAPI docs (Swagger UI)**
   - Visit: http://localhost:8000/docs
   - Click on `/api/auth/register` → Try it out → Execute
   - Copy the `access_token` from response
   - Click "Authorize" button (top right) → Enter: `Bearer YOUR_TOKEN`
   - Click on `/api/chat` → Try it out → Enter message → Execute

### Method 3: Quick Python REPL Test

```python
# In Python REPL or script
import asyncio
from langchain_core.messages import HumanMessage
from app.graph.workflow import my3_graph
from app.graph.state import AgentState

# Create test state
state: AgentState = {
    "messages": [HumanMessage(content="Hello")],
    "user_id": "test-123",
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
    "error": None
}

# Run workflow
result = await my3_graph.ainvoke(state)
print(result)
```

### Method 4: Verify Workflow Compilation Only

```python
# Quick check - no API calls needed
from app.graph.workflow import create_my3_workflow

graph = create_my3_workflow()
print("✅ Workflow compiled successfully!")
print(f"Graph type: {type(graph)}")
```

## What to Check

### ✅ Success Indicators:

1. **Workflow compiles** without errors
2. **All 6 nodes** are accessible
3. **Conditional routing** works:
   - Gift search → goes through: router → extract_person → check_recipient → generate_gifts → compose_response
   - Casual chat → goes through: router → compose_response (skips gift generation)
4. **AI responses** are generated
5. **Gift ideas** are created for gift_search intent
6. **Confirmation prompts** appear for add_recipient intent

### ⚠️ Common Issues:

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **OpenAI API errors**: Check `.env` file has `OPENAI_API_KEY` set

3. **Database errors**: Make sure PostgreSQL is running
   ```bash
   docker-compose up -d
   ```

4. **Type errors**: Check that AgentState matches the state structure

## Expected Test Results

### Test 1: Gift Search
- Input: "Gift ideas for my mom who loves gardening"
- Expected:
  - `current_intent`: "gift_search"
  - `detected_person`: {"relationship": "mom", "interests": ["gardening"]}
  - `gift_ideas`: List of 5 gift ideas
  - `requires_confirmation`: True (to add mom)
  - `ai_response`: Contains gift suggestions

### Test 2: Casual Chat
- Input: "Hello, how are you?"
- Expected:
  - `current_intent`: "casual_chat" or "unclear"
  - Skips gift generation (goes directly to compose_response)
  - `ai_response`: Friendly response

### Test 3: Add Recipient
- Input: "My wife Sarah loves yoga"
- Expected:
  - `current_intent`: "add_recipient"
  - `detected_person`: {"name": "Sarah", "relationship": "wife", "interests": ["yoga"]}
  - `requires_confirmation`: True
  - `pending_actions`: Contains create_recipient action

## Debugging Tips

1. **Check logs**: Look for workflow execution logs in console
2. **Print state**: Add print statements in nodes to see state changes
3. **Test individual nodes**: Import and test nodes separately
4. **Check routing**: Verify conditional routing functions return correct node names

## Next Steps

After testing Task 2.3:
- ✅ If tests pass → Proceed to next task
- ❌ If tests fail → Check error messages and fix issues
- ⚠️ If API calls fail → Verify OpenAI API key is set correctly

