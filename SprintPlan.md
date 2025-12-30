**PERFECT!** You've just solved the clutter problem. 10 relationships = **optimal for this design**. Let me update the complete sprint plan with this conversation-first, graph-as-background approach.

***

# **MY3 COMPLETE SPRINT PLAN - CONVERSATION-FIRST DESIGN**

## **Project Vision**

- **Two pages**: Landing + Dashboard
- **Chat-first**: All interactions through conversation
- **Network graph**: Interactive background (max 10 relationships)
- **No clutter**: No separate pages for CRUD operations

***

# **SPRINT 0: PROJECT SETUP (Day 1 - 4 hours)**

## **Goals**

✅ Backend and frontend projects initialized
✅ Database running locally
✅ Development environment ready

## **Tasks**

### **0.1: Initialize Backend (45 min)**

**Cursor Composer Prompt:**

```
Create a FastAPI + LangGraph backend for "My3" gift recommendation agent.

Project: my3-backend

Tech stack:
- FastAPI 0.104+
- LangGraph 0.0.40+
- LangChain + ChatOpenAI
- SQLAlchemy 2.0 async
- Alembic migrations
- PostgreSQL
- Pydantic v2
- Python 3.11+
- pytest + pytest-asyncio

Structure:
my3-backend/
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── alembic/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── graph/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── chat.py
│   │       └── recipients.py
│   └── utils/
│       ├── llm.py
│       └── auth.py
└── tests/

Database models:
1. User (id, email, name, hashed_password, created_at)
2. Recipient (id, user_id, name, relationship, age_band, interests[], constraints[], notes, created_at)
   - LIMIT: Max 10 recipients per user (add validation)
3. Occasion (id, user_id, recipient_id, name, occasion_type, date, budget_range, status, created_at)
4. GiftIdea (id, occasion_id, title, description, price, category, url, is_shortlisted, is_chosen, created_at)
5. Conversation (id, user_id, created_at)
6. Message (id, conversation_id, role, content, metadata, created_at)

API endpoints:
POST /api/auth/register
POST /api/auth/login
POST /api/chat
POST /api/chat/confirm
GET /api/recipients?user_id=xxx
GET /api/recipients/{id}
PUT /api/recipients/{id}
DELETE /api/recipients/{id}
GET /api/health

Include:
- Full async/await
- Type hints
- CORS middleware
- Logging
- Error handling
- docker-compose.yml with PostgreSQL

Generate complete project structure.
```


### **0.2: Initialize Frontend (45 min)**

**Cursor Composer Prompt:**

```
Create Next.js 15 frontend for "My3" - AI gift concierge with unique design.

Project: my3-frontend

Tech stack:
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- Shadcn/UI
- TanStack Query
- Framer Motion
- D3.js (for network graph)
- Zustand
- NextAuth.js

Structure:
my3-frontend/
├── .env.local.example
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx                # Landing page
│   ├── login/page.tsx
│   ├── register/page.tsx
│   └── dashboard/
│       └── page.tsx            # Main app (ONLY page after login)
├── components/
│   ├── landing/
│   │   ├── Hero.tsx
│   │   ├── Features.tsx
│   │   └── Demo.tsx
│   ├── dashboard/
│   │   ├── DashboardLayout.tsx # Graph + Chat combined
│   │   ├── NetworkGraph.tsx    # D3 background layer
│   │   ├── ChatWindow.tsx      # Center overlay
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   ├── GiftInlineCard.tsx  # Renders in chat
│   │   └── ConfirmationPrompt.tsx
│   └── ui/                     # Shadcn components
├── lib/
│   ├── api/
│   │   └── client.ts          # Single API client
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useChat.ts
│   │   └── useRecipients.ts
│   ├── store/
│   │   └── chatStore.ts
│   └── types.ts
└── public/

Design system:
- Primary: Warm gradient (#FF6B6B to #FFA07A)
- Background: Soft cream (#FFF9F5)
- Text: Charcoal (#2D3748)
- Accent: Teal (#14B8A6)
- Font: Inter

Key constraint:
- Dashboard is ONE page with graph + chat
- No separate pages for recipients/occasions/gifts
- Everything happens through conversation

Generate complete project with package.json.
```


### **0.3: Setup Development Environment (1 hour)**

```bash
# Backend
cd my3-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with OpenAI key

# Start PostgreSQL
docker-compose up -d

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
# Visit: http://localhost:8000/docs

# Frontend (new terminal)
cd ../my3-frontend
npm install
cp .env.local.example .env.local
# Edit .env.local

# Install Shadcn
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input textarea avatar badge dialog toast

# Start frontend
npm run dev
# Visit: http://localhost:3000
```


### **0.4: Verify Setup (30 min)**

- Backend /docs shows API endpoints
- Frontend landing page loads
- Database connection works
- Commit initial code

***

# **SPRINT 1: CORE AGENT + CHAT INTERFACE (Week 1-2)**

## **Sprint Goals**

✅ LangGraph workflow with 6 nodes working
✅ Chat API endpoint functional
✅ Dashboard with graph + chat rendered
✅ End-to-end conversation flow
✅ Max 10 recipients enforced

***

## **Day 1-3: Backend - Database \& LangGraph Core**

### **Task 1.1: SQLAlchemy Models (2 hours)**

**Cursor Prompt** (select `app/database/models.py`):

```
Create complete SQLAlchemy 2.0 async models:

1. User
   - id: UUID primary key
   - email: String unique indexed
   - name: String
   - hashed_password: String
   - created_at: DateTime
   - updated_at: DateTime

2. Recipient
   - id: UUID
   - user_id: UUID ForeignKey(user.id, ondelete="CASCADE")
   - name: String not null
   - relationship: String (mom, dad, wife, etc.)
   - age_band: String optional
   - interests: ARRAY(String) default []
   - constraints: ARRAY(String) default []
   - notes: Text optional
   - created_at: DateTime
   - updated_at: DateTime
   
   Add validation: Each user can have MAX 10 recipients
   (check in API layer, not database constraint)

3. Occasion
   - id: UUID
   - user_id: UUID ForeignKey
   - recipient_id: UUID ForeignKey(recipient.id, ondelete="CASCADE")
   - name: String
   - occasion_type: String
   - date: Date optional
   - budget_range: String optional
   - status: Enum("idea_needed", "shortlisted", "decided", "done")
   - created_at: DateTime
   - updated_at: DateTime

4. GiftIdea
   - id: UUID
   - occasion_id: UUID ForeignKey(occasion.id, ondelete="CASCADE")
   - title: String
   - description: Text
   - price: String
   - category: String
   - url: String
   - is_shortlisted: Boolean default False
   - is_chosen: Boolean default False
   - created_at: DateTime

5. Conversation
   - id: UUID
   - user_id: UUID ForeignKey
   - title: String optional
   - created_at: DateTime
   - updated_at: DateTime

6. Message
   - id: UUID
   - conversation_id: UUID ForeignKey
   - role: Enum("user", "assistant", "system")
   - content: Text
   - metadata: JSON optional (for gift_ideas, confirmations, etc.)
   - created_at: DateTime

Use async SQLAlchemy, proper relationships, indexes, __repr__ methods.
```


### **Task 1.2: Pydantic Schemas (1 hour)**

**Cursor Prompt** (select `app/database/schemas.py`):

```
Create Pydantic v2 schemas for API validation:

For each model (User, Recipient, Occasion, GiftIdea), create:
- Base schema (shared fields)
- Create schema (for POST)
- Update schema (for PUT, all optional)
- Response schema (includes id, timestamps)

Add custom validators:
- Email format
- URL format for gift links
- Recipient count limit (max 10)
- Future date validation for occasions
```


### **Task 1.3: Database Connection (30 min)**

**Cursor Prompt** (select `app/database/connection.py`):

```
Create async database utilities:

1. async_engine with proper pool settings
2. AsyncSessionLocal factory
3. get_db() FastAPI dependency
4. init_db() function
```


### **Task 1.4: Run Migrations (15 min)**

```bash
cd my3-backend
alembic revision --autogenerate -m "Initial schema with 10 recipient limit"
alembic upgrade head
```


***

## **Day 4-6: LangGraph Implementation**

### **Task 2.1: Agent State (1 hour)**

**Cursor Prompt** (select `app/graph/state.py`):

```
Create AgentState TypedDict for LangGraph:

from typing import TypedDict, List, Optional, Literal
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # Conversation
    messages: List[BaseMessage]
    user_id: str
    conversation_id: Optional[str]
    
    # Context (loaded from DB)
    user_recipients: List[dict]  # Max 10
    user_occasions: List[dict]
    
    # Current processing
    current_intent: Optional[Literal["gift_search", "add_recipient", "update_info", "casual_chat", "unclear"]]
    detected_person: Optional[dict]  # {name, relationship, interests, age_band}
    recipient_exists: Optional[bool]
    matched_recipient_id: Optional[str]
    
    # Actions to execute
    pending_actions: List[dict]
    requires_confirmation: bool
    confirmation_prompt: Optional[str]
    
    # Response
    ai_response: Optional[str]
    gift_ideas: Optional[List[dict]]
    error: Optional[str]
```


### **Task 2.2: Graph Nodes (4 hours)**

**Cursor Prompt** (select `app/graph/nodes.py`):

```
Create all 6 LangGraph nodes for My3 agent:

1. router_node(state: AgentState) -> dict
   - Classify user intent using ChatOpenAI with structured output
   - Return: {"current_intent": str}
   - Use Pydantic model for reliability

2. extract_person_node(state: AgentState) -> dict
   - Extract person info from message
   - Return: {"detected_person": {name, relationship, interests, age_band}}
   - Use structured LLM output

3. check_recipient_node(state: AgentState) -> dict
   - Check if detected_person exists in user_recipients
   - Match by name (fuzzy) or relationship (exact)
   - Return: {"recipient_exists": bool, "matched_recipient_id": str or None}

4. generate_gifts_node(state: AgentState) -> dict
   - Generate 5 personalized gift ideas using ChatOpenAI
   - Build context from recipient info
   - Return: {"gift_ideas": [GiftIdea]}
   - Use structured output for reliability

5. compose_response_node(state: AgentState) -> dict
   - Craft final AI response based on intent and data
   - Handle gift search, add recipient, update info, casual chat
   - Return: {
       "ai_response": str,
       "requires_confirmation": bool,
       "confirmation_prompt": str or None,
       "pending_actions": List[dict]
     }

6. execute_actions_node(state: AgentState) -> dict
   - Execute database operations (create recipient, update, etc.)
   - ENFORCE: Max 10 recipients per user (check before create)
   - Return: {"pending_actions": []}

All nodes:
- Use async/await
- Proper error handling
- Logging
- Type hints
- Comments explaining logic
```


### **Task 2.3: Workflow (1.5 hours)**

**Cursor Prompt** (select `app/graph/workflow.py`):

```
Create LangGraph workflow connecting all nodes:

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import *

def create_my3_workflow():
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("router", router_node)
    workflow.add_node("extract_person", extract_person_node)
    workflow.add_node("check_recipient", check_recipient_node)
    workflow.add_node("generate_gifts", generate_gifts_node)
    workflow.add_node("compose_response", compose_response_node)
    workflow.add_node("execute_actions", execute_actions_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Define conditional routing
    def route_after_router(state):
        intent = state["current_intent"]
        if intent in ["gift_search", "add_recipient", "update_info"]:
            return "extract_person"
        else:
            return "compose_response"
    
    def route_after_check(state):
        if state["current_intent"] == "gift_search":
            return "generate_gifts"
        else:
            return "compose_response"
    
    def route_after_compose(state):
        if state.get("requires_confirmation"):
            return END  # Wait for user confirmation
        elif state.get("pending_actions"):
            return "execute_actions"
        else:
            return END
    
    # Add edges
    workflow.add_conditional_edges("router", route_after_router)

---

# **SPRINT 1 CONTINUED**

***

## **Day 4-6: LangGraph Implementation (continued)**

### **Task 2.3: Workflow (continued)**

```python
    workflow.add_edge("extract_person", "check_recipient")
    workflow.add_conditional_edges("check_recipient", route_after_check)
    workflow.add_edge("generate_gifts", "compose_response")
    workflow.add_conditional_edges("compose_response", route_after_compose)
    workflow.add_edge("execute_actions", END)
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# Export compiled graph
my3_graph = create_my3_workflow()
```


***

## **Day 7-8: FastAPI Routes**

### **Task 3.1: Auth Routes (1 hour)**

**Cursor Prompt** (select `app/api/routes/auth.py`):

```
Create authentication endpoints:

POST /api/auth/register
- Body: {email: str, password: str, name: str}
- Validate email format and password strength
- Hash password with bcrypt
- Create user in database
- Return JWT access token

POST /api/auth/login
- Body: {email: str, password: str}
- Verify credentials
- Return JWT access token

Include:
- Proper error handling (400, 401, 409 for existing user)
- JWT token creation in app/utils/auth.py
- Token expiry: 7 days
```


### **Task 3.2: Chat Routes (2 hours)**

**Cursor Prompt** (select `app/api/routes/chat.py`):

```
Create chat endpoints:

POST /api/chat
- Body: {
    message: str,
    user_id: str,
    conversation_id?: str
  }
- Load user's recipients and occasions from database
- Initialize AgentState with:
  - messages: [HumanMessage(content=message)]
  - user_id
  - user_recipients: loaded from DB (max 10)
  - user_occasions: loaded from DB
- Invoke my3_graph.invoke(state, config)
- Return: {
    response: str,
    gift_ideas?: GiftIdea[],
    requires_confirmation?: bool,
    confirmation_prompt?: str,
    conversation_id: str,
    metadata?: dict
  }

POST /api/chat/confirm
- Body: {
    conversation_id: str,
    user_id: str,
    confirmed: bool
  }
- Load conversation state from checkpointer
- If confirmed=true:
  - Execute pending actions from state
  - Return success + updated recipient/occasion
- If confirmed=false:
  - Return acknowledgment
  - Clear pending actions

Include:
- Error handling
- Logging all LLM calls
- Conversation history management
- Token tracking
```


### **Task 3.3: Recipient Routes (1 hour)**

**Cursor Prompt** (select `app/api/routes/recipients.py`):

```
Create recipient endpoints (used by graph for display):

GET /api/recipients?user_id=xxx
- Return all user's recipients (max 10)
- Include count of upcoming occasions per recipient
- Sort by created_at descending

GET /api/recipients/{id}
- Return single recipient with full details
- Include occasions and past gifts

PUT /api/recipients/{id}
- Body: RecipientUpdate (all fields optional)
- Update recipient
- Return updated recipient

DELETE /api/recipients/{id}
- Soft delete or hard delete recipient
- Cascade delete occasions
- Return success message

IMPORTANT: Enforce 10 recipient limit in POST endpoint (handled by graph)
```


### **Task 3.4: Health Check (15 min)**

**Cursor Prompt** (select `app/api/routes/health.py`):

```
Create health check endpoint:

GET /api/health
- Return: {
    status: "healthy",
    database: "connected",
    timestamp: datetime
  }
- Test database connection
- Return 503 if database unavailable
```


### **Task 3.5: Wire Up Routes (30 min)**

**Cursor Prompt** (select `app/main.py`):

```
Update FastAPI main app:

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, chat, recipients, health

app = FastAPI(title="My3 Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://my3.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(recipients.router, prefix="/api/recipients", tags=["recipients"])
app.include_router(health.router, prefix="/api", tags=["health"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "My3 API - Your AI Gift Concierge"}

# Startup event
@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Database initialized")
```


***

## **Day 9-11: Frontend - Dashboard Layout**

### **Task 4.1: Dashboard Page Structure (2 hours)**

**Cursor Prompt** (select `app/dashboard/page.tsx`):

```
Create the main dashboard page - the ONLY page after login:

import { DashboardLayout } from "@/components/dashboard/DashboardLayout";

export default function DashboardPage() {
  return <DashboardLayout />;
}

This page renders the combined graph + chat interface.
User stays on this page for all interactions.
No navigation to other pages.
```


### **Task 4.2: Dashboard Layout Component (3 hours)**

**Cursor Prompt** (select `components/dashboard/DashboardLayout.tsx`):

```
Create DashboardLayout - the core UI combining graph + chat:

Layout:
┌─────────────────────────────────────────────────┐
│  Header (Logo, Search, Profile)                 │
├─────────────────────────────────────────────────┤
│                                                  │
│        NetworkGraph (Background Layer)           │
│                                                  │
│             ┌──────────────────┐                │
│    [Node]   │                  │   [Node]       │
│             │   ChatWindow     │                │
│             │   (Centered)     │                │
│   [Node]    │                  │                │
│             │   Messages       │    [Node]      │
│             │   [Gifts inline] │                │
│             │   Input          │                │
│             └──────────────────┘                │
│   [Node]                            [Node]      │
│                                                  │
└─────────────────────────────────────────────────┘

Components:
1. <NetworkGraph 
     recipients={recipients}
     activeRecipientId={activeChat}
     onNodeClick={(recipient) => handleNodeClick(recipient)}
   />
   - Renders D3.js force-directed graph
   - Full screen background (absolute positioned)
   - Semi-transparent nodes
   - Interactive clicks

2. <ChatWindow
     messages={messages}
     onSendMessage={handleSend}
     isLoading={isLoading}
     pendingConfirmation={pendingConfirmation}
   />
   - Centered overlay (absolute positioned)
   - Frosted glass effect (backdrop-filter: blur)
   - Width: 600px, height: 700px
   - z-index above graph

3. Header
   - Logo left
   - Search chat history (optional)
   - Profile dropdown right

State management:
- useRecipients(userId) - Fetch recipients (max 10)
- useChat(userId) - Handle messages
- useState for activeRecipientId
- When node clicked: Pre-fill chat input

Styling:
- Graph: opacity 0.6 normally, 0.2 when typing
- Chat: backdrop-filter: blur(20px), background: rgba(255,255,255,0.95)
- Smooth transitions

Use:
- TanStack Query for data
- Framer Motion for animations
- Responsive (mobile: chat full width, graph in drawer)
```


### **Task 4.3: NetworkGraph Component (4 hours)**

**Cursor Prompt** (select `components/dashboard/NetworkGraph.tsx`):

```
Create NetworkGraph component using D3.js:

Props:
- recipients: Recipient[] (max 10)
- activeRecipientId: string | null
- onNodeClick: (recipient: Recipient) => void

Design:
- Chat window position = center (no center "You" node needed)
- Recipients spread around chat in circle/organic pattern
- Force simulation with:
  - Center force (weak, toward screen center)
  - Collision force (nodes don't overlap)
  - Repulsion from chat window (400px radius exclusion zone)

Node design:
- Circle diameter: 80px
- Initials inside (2 letters)
- Color based on relationship:
  - Family (mom, dad, sibling): #FF6B6B (warm red)
  - Spouse/Partner (wife, husband): #FFA07A (coral)
  - Friends: #14B8A6 (teal)
  - Others: #CBD5E1 (gray)
- Border: 3px solid white
- Shadow: 0 4px 12px rgba(0,0,0,0.1)
- Red dot badge if occasion within 30 days (top-right corner)

Node states:
- Default: opacity 0.7
- Hover: opacity 1, scale 1.1, cursor pointer
- Active (in current chat): opacity 1, pulsing animation, glow
- Typing: All nodes fade to opacity 0.2

Connections:
- NO lines between nodes (cleaner)
- Or: Very subtle dotted lines to chat window (optional)

Interactions:
- Click node → calls onNodeClick(recipient)
- Hover → Tooltip shows:
  - Name
  - Next occasion (if any): "Birthday in 15 days"
  - Last gift given (if any)
- Drag → Node moves but springs back (physics)

Performance:
- Limit force simulation to 100 ticks
- Use requestAnimationFrame
- Pause simulation when not visible
- Use CSS transforms for GPU acceleration

Responsive:
- Desktop: Full screen background
- Tablet: Fewer nodes visible, smaller
- Mobile: Hide graph OR show as thumbnail overlay

Implementation:
- Use React ref for SVG container
- D3.js for force simulation
- Framer Motion for node animations
- useEffect for simulation lifecycle

Empty state:
- When 0 recipients: Show ghost nodes with labels
  - "Add your first person"
  - "Try: 'My mom loves gardening'"
```


### **Task 4.4: ChatWindow Component (3 hours)**

**Cursor Prompt** (select `components/dashboard/ChatWindow.tsx`):

```
Create ChatWindow component - the center overlay:

Props:
- messages: Message[]
- onSendMessage: (message: string) => Promise<void>
- isLoading: boolean
- pendingConfirmation: PendingConfirmation | null
- preFillMessage?: string (from node click)

Layout:
┌─────────────────────────────┐
│  Chat with My3    [_ □ ×]   │ ← Header (draggable?)
├─────────────────────────────┤
│  Messages area              │
│  [Auto-scroll]              │
│                             │
│  💬 User message            │
│                             │
│  🤖 My3 response            │
│     [Gift cards inline]     │
│     [Yes/No buttons]        │
│                             │
│  💬 User message            │
│                             │
│  🤖 My3 response            │
│  ...                        │
├─────────────────────────────┤
│  [Type message...    ] 📤   │ ← Input
└─────────────────────────────┘

Styling:
.chat-window {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  height: 700px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  flex-direction: column;
  z-index: 100;
}

Messages section:
- Flex-1, overflow-y-auto
- User messages: right-aligned, blue bubble
- AI messages: left-aligned, gray bubble
- Timestamps on hover
- Auto-scroll to bottom on new message
- Loading indicator (3 dots animation)

Inline content:
- Gift cards render inside AI messages
- Confirmation buttons (Yes/No) render inline
- Images (if any) render inline

Input section:
- Textarea that grows with content (max 150px)
- Send button (disabled when empty or loading)
- "Shift+Enter" for newline, "Enter" to send
- Show "My3 is typing..." when loading

Pre-fill behavior:
- When preFillMessage prop changes, set input value
- Focus input automatically
- Clear pre-fill after first message

Use:
- Shadcn Textarea, Button, Avatar
- Framer Motion for message entrance
- react-textarea-autosize
- Auto-focus on mount

Responsive:
- Desktop: 600x700px centered
- Tablet: 80% width, 600px height
- Mobile: Full width minus 20px margins, 70vh height
```


***

## **Day 12-14: Chat Features \& Integration**

### **Task 4.5: ChatMessage Component (1.5 hours)**

**Cursor Prompt** (select `components/dashboard/ChatMessage.tsx`):

```
Create ChatMessage component for individual messages:

Props:
- message: Message {
    role: "user" | "assistant"
    content: string
    metadata?: {
      gift_ideas?: GiftIdea[]
      requires_confirmation?: bool
      confirmation_prompt?: string
    }
    created_at: Date
  }
- onConfirm?: (confirmed: boolean) => void

Rendering logic:
1. If role === "user":
   - Right-aligned blue bubble
   - User avatar on right

2. If role === "assistant":
   - Left-aligned gray bubble
   - My3 avatar (logo) on left
   - If metadata.gift_ideas exists:
     - Render <GiftInlineCard /> for each gift
   - If metadata.requires_confirmation:
     - Show confirmation prompt text
     - Render Yes/No buttons below
     - On click: call onConfirm(true/false)

Styling:
- Max width: 80%
- Padding: 12px 16px
- Border radius: 16px
- Markdown support for content (bold, italic, lists)
- Smooth entrance animation

Use:
- Shadcn Avatar, Button
- react-markdown for formatting
- Framer Motion for animation
```


### **Task 4.6: GiftInlineCard Component (2 hours)**

**Cursor Prompt** (select `components/dashboard/GiftInlineCard.tsx`):

```
Create GiftInlineCard - renders gift ideas in chat:

Props:
- gift: GiftIdea {
    title: string
    description: string
    price: string
    category: string
    url: string
  }
- compact?: boolean (for smaller views)

Layout (horizontal):
┌──────────────────────────────────────┐
│

---

# **SPRINT 1 CONTINUED**

***

## **Day 12-14: Chat Features & Integration (continued)**

### **Task 4.6: GiftInlineCard Component (continued)**

```

Layout (horizontal):
┌──────────────────────────────────────────────┐
│  [Icon]  Gift Title          \$XX.XX         │
│   80px   Description...       [View] [♡]    │
│          Category                            │
└──────────────────────────────────────────────┘

Design:

- Width: 100% of chat message
- Height: 100px
- Background: White with subtle border
- Border radius: 12px
- Hover: Lift shadow effect

Left side:

- Icon or category image (80x80px)
- Fallback: Category emoji (🎁, 📚, ☕, etc.)

Right side:

- Title: Bold, 16px
- Price: Right-aligned, accent color (\#FF6B6B)
- Description: 2 lines max with ellipsis
- Category badge: Small, gray pill
- Actions:
    - "View \& Buy" button (opens URL in new tab)
    - Heart icon for shortlist (optional, for later)

Props:

- gift: GiftIdea
- compact: boolean (reduces height to 80px)

Styling:

- Card animation: Slide in from bottom
- Hover: Scale 1.02, shadow increase
- Responsive: Stack vertically on mobile

Use Shadcn Card, Button, Badge.

```

### **Task 4.7: useChat Hook (2 hours)**

**Cursor Prompt** (select `lib/hooks/useChat.ts`):
```

Create useChat hook for chat state management:

export function useChat(userId: string) {
const [messages, setMessages] = useState<Message[]>([]);
const [conversationId, setConversationId] = useState<string | null>(null);
const [pendingConfirmation, setPendingConfirmation] = useState<PendingConfirmation | null>(null);

const queryClient = useQueryClient();

// Send message mutation
const sendMessageMutation = useMutation({
mutationFn: async (message: string) => {
return chatAPI.sendMessage({
message,
user_id: userId,
conversation_id: conversationId
});
},
onMutate: (message) => {
// Optimistic update: Add user message immediately
const userMessage: Message = {
id: crypto.randomUUID(),
role: "user",
content: message,
created_at: new Date()
};
setMessages(prev => [...prev, userMessage]);
},
onSuccess: (data) => {
// Add AI response
const aiMessage: Message = {
id: crypto.randomUUID(),
role: "assistant",
content: data.response,
metadata: {
gift_ideas: data.gift_ideas,
requires_confirmation: data.requires_confirmation,
confirmation_prompt: data.confirmation_prompt
},
created_at: new Date()
};
setMessages(prev => [...prev, aiMessage]);

      // Set conversation ID
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }
      
      // Handle confirmation prompt
      if (data.requires_confirmation) {
        setPendingConfirmation({
          conversationId: data.conversation_id,
          prompt: data.confirmation_prompt
        });
      }
      
      // Invalidate recipients cache (might have been added)
      queryClient.invalidateQueries(['recipients', userId]);
    },
    onError: (error) => {
      toast.error("Failed to send message");
      console.error(error);
    }
    });

// Confirm action mutation
const confirmMutation = useMutation({
mutationFn: async (confirmed: boolean) => {
return chatAPI.confirm({
conversation_id: conversationId!,
user_id: userId,
confirmed
});
},
onSuccess: (data) => {
setPendingConfirmation(null);

      // Add system message
      const systemMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.message,
        created_at: new Date()
      };
      setMessages(prev => [...prev, systemMessage]);
      
      // Refresh recipients
      queryClient.invalidateQueries(['recipients', userId]);
      
      toast.success(data.message);
    }
    });

return {
messages,
sendMessage: sendMessageMutation.mutate,
confirmAction: confirmMutation.mutate,
isLoading: sendMessageMutation.isPending,
pendingConfirmation,
conversationId
};
}

```

### **Task 4.8: useRecipients Hook (1 hour)**

**Cursor Prompt** (select `lib/hooks/useRecipients.ts`):
```

Create useRecipients hook:

export function useRecipients(userId: string) {
const { data: recipients, isLoading, error } = useQuery({
queryKey: ['recipients', userId],
queryFn: () => recipientAPI.list(userId),
staleTime: 5 * 60 * 1000, // 5 minutes
});

return {
recipients: recipients || [],
isLoading,
error,
count: recipients?.length || 0,
hasMaxRecipients: (recipients?.length || 0) >= 10
};
}

```

### **Task 4.9: API Client (1.5 hours)**

**Cursor Prompt** (select `lib/api/client.ts`):
```

Create API client with axios:

import axios from 'axios';

const apiClient = axios.create({
baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
headers: {
'Content-Type': 'application/json'
}
});

// Add auth token interceptor
apiClient.interceptors.request.use((config) => {
const token = localStorage.getItem('auth_token');
if (token) {
config.headers.Authorization = `Bearer ${token}`;
}
return config;
});

// Chat API
export const chatAPI = {
sendMessage: async (data: {
message: string;
user_id: string;
conversation_id?: string;
}) => {
const response = await apiClient.post('/api/chat', data);
return response.data;
},

confirm: async (data: {
conversation_id: string;
user_id: string;
confirmed: boolean;
}) => {
const response = await apiClient.post('/api/chat/confirm', data);
return response.data;
}
};

// Recipients API
export const recipientAPI = {
list: async (userId: string) => {
const response = await apiClient.get(`/api/recipients?user_id=${userId}`);
return response.data;
},

get: async (id: string) => {
const response = await apiClient.get(`/api/recipients/${id}`);
return response.data;
},

update: async (id: string, data: any) => {
const response = await apiClient.put(`/api/recipients/${id}`, data);
return response.data;
},

delete: async (id: string) => {
const response = await apiClient.delete(`/api/recipients/${id}`);
return response.data;
}
};

// Auth API
export const authAPI = {
register: async (data: {
email: string;
password: string;
name: string;
}) => {
const response = await apiClient.post('/api/auth/register', data);
return response.data;
},

login: async (data: {
email: string;
password: string;
}) => {
const response = await apiClient.post('/api/auth/login', data);
return response.data;
}
};

```

***

## **Day 15: Testing & Bug Fixes**

### **Task 5.1: Backend Testing (2 hours)**

**Cursor Prompt** (create `tests/test_graph/test_workflow.py`):
```

Create pytest tests for LangGraph workflow:

import pytest
from app.graph.workflow import my3_graph
from app.graph.state import AgentState
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_gift_search_flow():
"""Test complete gift search flow"""
state = AgentState(
messages=[HumanMessage(content="Gift ideas for my mom who loves gardening")],
user_id="test-user-123",
conversation_id=None,
user_recipients=[],
user_occasions=[],
current_intent=None,
detected_person=None,
recipient_exists=None,
matched_recipient_id=None,
pending_actions=[],
requires_confirmation=False,
confirmation_prompt=None,
ai_response=None,
gift_ideas=None,
error=None
)

    result = await my3_graph.ainvoke(state)
    
    assert result["current_intent"] == "gift_search"
    assert result["detected_person"]["relationship"] == "mom"
    assert result["gift_ideas"] is not None
    assert len(result["gift_ideas"]) == 5
    assert result["requires_confirmation"] == True  # Should ask to add mom
    @pytest.mark.asyncio
async def test_add_recipient_flow():
"""Test adding new recipient"""
\# Test with explicit "add" intent
\# Verify recipient is created
\# Check max 10 limit

@pytest.mark.asyncio
async def test_existing_recipient():
"""Test gift search for existing recipient"""
\# Provide existing recipients in state
\# Verify no confirmation prompt
\# Verify gift ideas generated

# Add more tests for each node

```

### **Task 5.2: Frontend Manual Testing (2 hours)**

Test scenarios:
1. **First user flow**:
   - Sign up
   - Dashboard loads with empty graph
   - Send: "My mom loves coffee"
   - Verify: Gifts appear, confirmation prompt
   - Click "Yes"
   - Verify: Mom node appears in graph

2. **Existing recipient flow**:
   - Click Mom node in graph
   - Verify: Chat pre-fills "Gift ideas for Mom"
   - Send message
   - Verify: Gifts appear, no confirmation

3. **Max 10 recipients**:
   - Add 10 recipients through chat
   - Try to add 11th
   - Verify: Error message

4. **Mobile responsive**:
   - Test on mobile viewport
   - Verify chat works
   - Verify graph is hidden or in drawer

### **Task 5.3: Bug Fixes (2 hours)**

Fix any issues found during testing:
- Graph nodes overlapping chat
- Chat not scrolling correctly
- LLM responses formatting
- API errors
- Loading states

***

## **Sprint 1 Demo & Retrospective (End of Week 2)**

### **Demo Checklist**:
✅ User can sign up and login  
✅ Dashboard shows empty graph on first load  
✅ User can chat with My3  
✅ My3 generates gift ideas  
✅ My3 asks to add new people  
✅ Confirmation flow works  
✅ Recipients appear in graph (max 10)  
✅ Clicking node pre-fills chat  
✅ Mobile responsive  

***

# **SPRINT 2: POLISH & SMART FEATURES (Week 3-4)**

## **Sprint Goals**
✅ Auto-update recipient info from conversation  
✅ Occasion tracking and reminders  
✅ Graph enhancements (animations, tooltips)  
✅ Landing page with demo  
✅ Dark mode  
✅ Performance optimization  

***

## **Day 16-17: Auto-Update Intelligence**

### **Task 6.1: Enhanced Agent Logic (3 hours)**

**Cursor Prompt** (update `app/graph/nodes.py` - compose_response_node):
```

Enhance compose_response_node to handle auto-updates:

When user says facts about existing people:

- "My wife's birthday is June 5"
- "Sarah loves yoga and reading"
- "Dad doesn't drink alcohol"

Logic:

1. If recipient exists AND new info detected:
    - Don't ask for confirmation
    - Auto-add to pending_actions:
{
"type": "update_recipient",
"recipient_id": xxx,
"updates": {
"interests": ["yoga", "reading"],  // Append, don't replace
}
}
OR
{
"type": "create_occasion",
"recipient_id": xxx,
"occasion_data": {
"name": "Wife's Birthday",
"occasion_type": "birthday",
"date": "2026-06-05"
}
}
2. Respond naturally:
    - "Got it! I'll remember Sarah loves yoga and reading."
    - "Noted - your wife's birthday is June 5. I'll remind you next year!"
3. Execute actions immediately (no confirmation needed for updates)

Add to execute_actions_node:

- Handle "update_recipient" action (merge new data)
- Handle "create_occasion" action

```

### **Task 6.2: Proactive Reminders (2 hours)**

**Cursor Prompt** (create `app/utils/reminders.py`):
```

Create reminder system:

async def check_upcoming_occasions(user_id: str) -> List[dict]:
"""
Check for occasions in next 30 days
Return list of reminders
"""
\# Query occasions where:
\# - user_id matches
\# - date is between today and +30 days
\# - status != "done"

    # Return: [
    #   {
    #     "recipient_name": "Mom",
    #     "occasion": "Birthday",
    #     "date": "2026-04-16",
    #     "days_until": 15,
    #     "has_gift": false
    #   }
    # ]
    
# Call this when user opens chat

# Show reminders at top of chat:

# "🎂 Reminder: Your mom's birthday is in 15 days. Need gift ideas?"

```

### **Task 6.3: Context Injection (1 hour)**

**Cursor Prompt** (update `app/api/routes/chat.py`):
```

Enhance chat endpoint to inject reminders:

When user sends first message of session:

1. Check for upcoming occasions (next 30 days)
2. If any found, prepend system message:

SystemMessage(
content=f"CONTEXT: User has upcoming occasions: {reminders}.
Mention these proactively if relevant to conversation."
)
3. This helps AI remember to bring up occasions naturally
```

***

## **Day 18-19: Graph Enhancements**

### **Task 7.1: Enhanced Tooltips (2 hours)**

**Cursor Prompt** (update `components/dashboard/NetworkGraph.tsx`):
```

Add rich tooltips to network nodes:

On hover, show floating tooltip:
┌─────────────────────────┐
│  Mom                    │
│  ━━━━━━━━━━━━━━━       │
│  🎂 Birthday: Apr 16    │
│  ⏰ In 15 days          │
│  🎁 Last gift: Coffee   │
│                         │
│  Click for gift ideas   │
└─────────────────────────┘

Design:

- Floating card above node
- Smooth fade in (200ms)
- Arrow pointing to node
- Use Shadcn Tooltip

---

# **SPRINT 2 CONTINUED**


***

## **Day 18-19: Graph Enhancements (continued)**

### **Task 7.1: Enhanced Tooltips (continued)**

```typescript
Content:
- Recipient name (bold)
- Next occasion with countdown
- Last gift given (if any)
- "Click for gift ideas" hint

Positioning:
- Above node if space available
- Below if near top edge
- Auto-adjust to stay in viewport

Use Framer Motion for animation.
Add pointer arrow to tooltip.
```


### **Task 7.2: Node Animations (2 hours)**

**Cursor Prompt** (update `components/dashboard/NetworkGraph.tsx`):

```
Add animations to network nodes:

1. Urgency Pulse:
   - If occasion within 7 days: Gentle pulse animation
   - Red outer ring that expands/contracts
   - Draws attention without being annoying

2. New Node Entrance:
   - When recipient added: Node fades in from center
   - Expands to full size over 500ms
   - Other nodes adjust smoothly

3. Active Conversation Glow:
   - When clicking node: Add glow effect
   - Thicker border, shadow increase
   - Connection line (if using lines) highlights

4. Hover States:
   - Scale: 1.0 → 1.1 (100ms ease-out)
   - Shadow: Increase depth
   - Cursor: pointer
   - Tooltip appears

5. Graph Fade on Typing:
   - When user focuses input: All nodes fade to 0.2 opacity
   - When blur: Fade back to 0.7
   - Smooth 300ms transition

CSS:
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7);
  }
  50% {
    box-shadow: 0 0 0 12px rgba(255, 107, 107, 0);
  }
}

.node.urgent {
  animation: pulse 2s infinite;
}
```


### **Task 7.3: Graph Empty State (1 hour)**

**Cursor Prompt** (update `components/dashboard/NetworkGraph.tsx`):

```
Create beautiful empty state when 0 recipients:

Show ghost nodes (3-4) with labels:
1. "Add your first person"
   - Position: Right of chat
   - Dashed circle outline
   - Label inside
   
2. "Try: 'My mom loves gardening'"
   - Position: Left of chat
   - Speech bubble style
   
3. "Build your network"
   - Position: Top
   - Icon + text

Animation:
- Gentle floating motion
- Fade in on mount
- Not clickable (visual guide only)

Once user adds first recipient:
- Ghost nodes fade out
- Real nodes fade in
```


***

## **Day 20-21: Landing Page**

### **Task 8.1: Hero Section (2 hours)**

**Cursor Prompt** (create `components/landing/Hero.tsx` and update `app/page.tsx`):

```
Create landing page hero section:

Layout:
┌─────────────────────────────────────────┐
│                                         │
│        Your AI Gift Concierge           │
│    Never forget a birthday again        │
│                                         │
│    [Try Demo] [Sign Up Free]           │
│                                         │
│       [Demo Chat Interface]             │
│    (Interactive, no signup needed)      │
│                                         │
└─────────────────────────────────────────┘

Content:
- Headline: "Your AI Gift Concierge"
- Subheadline: "Remember every birthday, find perfect gifts, build stronger relationships"
- CTAs: 
  - Primary: "Get Started Free"
  - Secondary: "Try Demo" (scrolls to demo)

Design:
- Gradient background (cream to light coral)
- Large, bold typography (Inter font)
- Animated network graph in background (subtle)
- Mobile responsive

Use Framer Motion for scroll animations.
```


### **Task 8.2: Demo Chat Section (3 hours)**

**Cursor Prompt** (create `components/landing/DemoChat.tsx`):

```
Create interactive demo chat (no login required):

Features:
1. Pre-built demo conversation:
   - Shows example interaction
   - User: "My mom's birthday is coming up"
   - My3: "When is her birthday?"
   - User: "April 16, she loves gardening"
   - My3: [Shows gift ideas]

2. Users can try their own messages:
   - Limited to 5 messages per session
   - No data saved (mock responses)
   - After 5 messages: CTA to sign up

3. Visual design:
   - Same ChatWindow component
   - Smaller size (500x600px)
   - "DEMO" badge in corner
   - Mock network graph behind (3-4 example nodes)

Mock responses:
- Use simple keyword matching
- "mom" → Show gardening gifts
- "dad" → Show tech gifts
- "birthday" → Show birthday gift ideas
- Default: Generic response + CTA to sign up

No backend calls needed (client-side only).
```


### **Task 8.3: Features Section (1.5 hours)**

**Cursor Prompt** (create `components/landing/Features.tsx`):

```
Create features showcase:

3-column grid:

┌──────────────┬──────────────┬──────────────┐
│ 🤖 AI-Powered│ 🕸️ Network   │ 📅 Reminders │
│              │              │              │
│ Smart gift   │ Visualize    │ Never miss   │
│ suggestions  │ relationships│ a birthday   │
└──────────────┴──────────────┴──────────────┘

Each feature:
- Icon (emoji or custom)
- Title
- Short description (2 sentences)
- Subtle hover effect

Design:
- Card-based layout
- Consistent spacing
- Icons with gradient background
- Mobile: Stack vertically
```


### **Task 8.4: Footer \& Navigation (1 hour)**

**Cursor Prompt** (update `app/page.tsx`):

```
Add navigation header and footer:

Header (sticky):
- Logo left
- Nav links: Features, Demo, Pricing (future)
- "Login" and "Sign Up" buttons right

Footer:
- Logo + tagline
- Links: Privacy, Terms, Contact
- Social media icons (optional)
- "Made with ❤️ by [Your Name]"

Use Shadcn Button, Link components.
```


***

## **Day 22-23: Authentication \& Settings**

### **Task 9.1: Login/Register Pages (2 hours)**

**Cursor Prompt** (create `app/login/page.tsx` and `app/register/page.tsx`):

```
Create auth pages:

Login Page:
- Email input
- Password input
- "Remember me" checkbox
- "Forgot password?" link
- "Login" button
- "Don't have account? Sign up" link

Register Page:
- Name input
- Email input
- Password input
- "I agree to Terms" checkbox
- "Sign Up" button
- "Already have account? Login" link

Design:
- Centered card (400px width)
- Gradient background
- Form validation (Zod + react-hook-form)
- Loading states
- Error messages

Use Shadcn Form, Input, Button, Checkbox.

On success:
- Save JWT to localStorage
- Redirect to /dashboard
```


### **Task 9.2: Protected Routes (1 hour)**

**Cursor Prompt** (create `app/dashboard/layout.tsx`):

```
Add authentication middleware:

import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const token = cookies().get('auth_token');
  
  if (!token) {
    redirect('/login');
  }
  
  return <>{children}</>;
}

Also create middleware.ts at root:
- Check auth on /dashboard routes
- Redirect to /login if not authenticated
```


### **Task 9.3: User Profile Dropdown (1.5 hours)**

**Cursor Prompt** (create `components/dashboard/ProfileDropdown.tsx`):

```
Create profile dropdown in dashboard header:

Trigger: User avatar + name (top right)

Menu items:
- User name (not clickable, header)
- Settings (future)
- Export Data (future)
- Separator
- Dark Mode Toggle
- Separator
- Logout

On logout:
- Clear localStorage
- Clear auth cookies
- Redirect to landing page

Use Shadcn DropdownMenu, Avatar, Separator.
```


***

## **Day 24-25: Dark Mode \& Polish**

### **Task 10.1: Dark Mode Implementation (2 hours)**

**Cursor Prompt** (update `app/layout.tsx` and theme):

```
Add dark mode support:

1. Install next-themes:
   npm install next-themes

2. Wrap app in ThemeProvider:
   import { ThemeProvider } from 'next-themes'
   
   <ThemeProvider attribute="class" defaultTheme="light">
     {children}
   </ThemeProvider>

3. Update Tailwind config:
   darkMode: 'class'

4. Create dark mode variants:
   
   Light mode:
   - Background: #FFF9F5 (cream)
   - Chat: rgba(255, 255, 255, 0.95)
   - Text: #2D3748
   
   Dark mode:
   - Background: #1A202C
   - Chat: rgba(26, 32, 44, 0.95)
   - Text: #E2E8F0
   - Graph nodes: Darker colors

5. Update all components with dark: variants:
   - ChatWindow: dark:bg-gray-900 dark:text-gray-100
   - NetworkGraph: Adjust node colors
   - Cards, buttons, etc.

6. Add toggle in ProfileDropdown:
   - Sun/Moon icon
   - Switch between light/dark
   - Save preference to localStorage
```


### **Task 10.2: Loading States \& Skeletons (2 hours)**

**Cursor Prompt** (create `components/ui/LoadingState.tsx`):

```
Add loading states throughout:

1. Dashboard loading:
   - Skeleton network graph (pulsing circles)
   - Skeleton chat window
   - Show while fetching recipients

2. Message sending:
   - "My3 is thinking..." with animated dots
   - Disable input while loading

3. Gift cards loading:
   - Skeleton cards (gray rectangles pulsing)

4. Auth pages:
   - Spinner on button during submit

Use Shadcn Skeleton component.
Add smooth transitions between loading and loaded states.
```


### **Task 10.3: Error Handling \& Toasts (1.5 hours)**

**Cursor Prompt** (update error handling across app):

```
Add comprehensive error handling:

1. API errors:
   - Network error: "Connection failed. Please try again."
   - 401 Unauthorized: Redirect to login
   - 403 Forbidden: "You don't have permission"
   - 404 Not Found: "Resource not found"
   - 500 Server Error: "Something went wrong. Please try again."
   - 429 Rate Limit: "Too many requests. Please wait."

2. LLM errors:
   - OpenAI timeout: "Request took too long. Please try again."
   - No response: "Couldn't generate response. Please rephrase."

3. Validation errors:
   - Max 10 recipients: "You've reached the maximum of 10 important people. Delete one to add another."
   - Empty message: "Please enter a message"
   - Invalid email: "Please enter a valid email"

4. Success messages:
   - Recipient added: "Added [Name] to your network!"
   - Occasion created: "Saved [Occasion]"
   - Gift shortlisted: "Added to your shortlist"

Use Sonner for toasts:
   npm install sonner
   
Add <Toaster /> to root layout.
Use toast.success(), toast.error(), toast.info().
```


### **Task 10.4: Performance Optimization (2 hours)**

**Cursor Prompt** (optimize across app):

```
Optimize performance:

1. Frontend:
   - Lazy load D3.js (dynamic import)
   - Memo expensive components (NetworkGraph)
   - Debounce chat input (don't send on every keystroke)
   - Virtual scrolling for long message lists (react-window)
   - Image optimization (next/image for gift cards)
   - Code splitting (dynamic imports for landing page)

2. Backend:
   - Add database indexes:
     - user_id on recipients, occasions
     - created_at on messages
   - Cache recipient queries (5 min TTL)
   - Batch database operations in execute_actions_node
   - Add request timeout (30s max)
   - Connection pooling (already in SQLAlchemy)

3. LLM optimization:
   - Use streaming responses (for future)
   - Reduce token usage in prompts
   - Cache common queries (future)

4. Bundle size:
   - Analyze with next/bundle-analyzer
   - Tree-shake unused dependencies
   - Minimize D3.js imports (only import needed functions)

Run Lighthouse audit:
- Target: 90+ performance score
- Fix any issues found
```


***

## **Day 26-28: Final Testing \& Bug Fixes**

### **Task 11.1: End-to-End Testing (3 hours)**

**Test Scenarios:**

1. **Complete New User Journey**:
    - Visit landing page
    - Try demo (send 3 messages)
    - Click "Sign Up"
    - Register with email
    - Redirected to dashboard (empty state)
    - Send: "My mom loves gardening, her birthday is April 16"
    - Verify: Gifts appear
    - Click "Yes" to add mom
    - Verify: Mom node appears in graph
    - Click mom node
    - Verify: Chat pre-fills
    - Send message
    - Verify: More gifts appear, no confirmation
2. **Multiple Recipients**:
    - Add 10 recipients through chat
    - Verify: All appear in graph
    - Try to add 11th
    - Verify: Error message
    - Delete one recipient
    - Verify: Can now add 11th
3. **Occasion Tracking**:
    - Add recipient with birthday date
    - Verify: Occasion created in database
    - Check graph node has red dot (if within 30 days)
    - Hover node
    - Verify: Tooltip shows countdown
4. **Dark Mode**:
    - Toggle dark mode
    - Verify: All components adapt
    - Refresh page
    - Verify: Preference persists
5. **Mobile Experience**:
    - Test on mobile viewport (375px)
    - Verify: Chat full width
    - Verify: Graph accessible (drawer/overlay)
    - Verify: All features work
6. **Error Handling**:
    - Disconnect from internet
    - Send message
    - Verify: Error toast appears
    - Reconnect
    - Retry
    - Verify: Works

### **Task 11.2: Bug Fixes (3 hours)**

Fix any issues found:

- [ ] Graph nodes overlapping chat
- [ ] Messages not scrolling
- [ ] API timeout handling
- [ ] Loading states missing
- [ ] Mobile layout issues
- [ ] Dark mode glitches
- [ ] Authentication edge cases


### **Task 11.3: Documentation (2 hours)**

**Cursor Prompt** (create/update README files):

```
Create comprehensive documentation:

Backend README (my3-backend/README.md):
- Project overview
- Setup instructions
- Environment variables
- Database migrations
- Running locally
- API documentation
- Testing
- Deployment

Frontend README (my3-frontend/README.md):
- Project overview
- Setup instructions
- Environment variables
- Running locally
- Building for production
- Deployment

Root README:
- Project

---

# is there anything else?

Great question! Let me complete the sprint plan and add the critical remaining pieces:

***

# **SPRINT 2 CONTINUED - FINAL PIECES**

## **Day 26-28: Documentation & Deployment Prep (continued)**

### **Task 11.3: Documentation (continued)**

```markdown
Root README.md:
# My3 - Your AI Gift Concierge

## Overview
AI-powered gift recommendation agent that helps you remember important people, 
occasions, and find perfect gifts through natural conversation.

## Key Features
- 🤖 Conversational AI (powered by LangGraph)
- 🕸️ Visual relationship network (D3.js)
- 🎁 Personalized gift suggestions
- 📅 Birthday reminders
- ✨ Remembers preferences automatically
- 📱 Mobile-friendly

## Tech Stack
- **Backend**: FastAPI + LangGraph + PostgreSQL
- **Frontend**: Next.js 15 + TypeScript + Tailwind
- **Deployment**: Railway (backend) + Vercel (frontend)

## Quick Start
See `/my3-backend/README.md` and `/my3-frontend/README.md`

## Architecture
[Add architecture diagram]

## License
MIT
```


***

# **SPRINT 3: DEPLOYMENT \& LAUNCH (Week 5-6)**

## **Sprint Goals**

✅ Deploy backend to Railway
✅ Deploy frontend to Vercel
✅ Set up monitoring \& analytics
✅ Launch to first users
✅ Gather feedback

***

## **Day 29-30: Backend Deployment**

### **Task 12.1: Prepare for Production (2 hours)**

**Cursor Prompt** (create production configs):

```
Create production configurations:

1. Update app/config.py:
   - Add production environment check
   - Disable debug mode in production
   - Set secure CORS origins
   - Configure logging (structured JSON logs)

2. Create Dockerfile (for Railway):
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]

3. Create .dockerignore:
venv/
__pycache__/
*.pyc
.env
.git/
tests/

4. Update alembic for production:
   - Use DATABASE_URL from environment
   - Auto-run migrations on deploy (optional)

5. Add health check endpoint logs
```


### **Task 12.2: Deploy to Railway (2 hours)**

**Steps:**

```bash
1. Create Railway account (railway.app)

2. Create new project:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect my3-backend repo
   - Railway auto-detects Python

3. Add PostgreSQL database:
   - Click "New" → "Database" → "PostgreSQL"
   - Railway provisions database
   - Sets DATABASE_URL automatically

4. Set environment variables:
   - OPENAI_API_KEY=sk-...
   - SECRET_KEY=(generate secure key)
   - ALLOWED_ORIGINS=https://my3.vercel.app
   - ENVIRONMENT=production

5. Deploy:
   - Railway builds and deploys automatically
   - Get deployment URL: https://my3-backend.railway.app

6. Run migrations:
   - Railway CLI: railway run alembic upgrade head
   - Or: Add to Dockerfile CMD

7. Test API:
   - Visit https://my3-backend.railway.app/docs
   - Test /api/health endpoint
   - Verify database connection
```


### **Task 12.3: Set Up Railway Monitoring (1 hour)**

- Enable Railway logs
- Set up alerts for errors
- Monitor memory/CPU usage
- Set up auto-scaling (if needed)

***

## **Day 31-32: Frontend Deployment**

### **Task 13.1: Prepare Frontend for Production (1 hour)**

**Cursor Prompt:**

```
Production optimizations:

1. Update next.config.js:
module.exports = {
  reactStrictMode: true,
  compress: true,
  images: {
    domains: ['my3-backend.railway.app'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
}

2. Add analytics (optional):
   - Vercel Analytics (built-in)
   - Or Plausible/PostHog for privacy-friendly analytics

3. Add error tracking:
   - Sentry (optional)
   - Or simple error logging

4. Environment variables:
   - NEXT_PUBLIC_API_URL=https://my3-backend.railway.app
   - NEXTAUTH_URL=https://my3.vercel.app
   - NEXTAUTH_SECRET=(generate)

5. Build test:
   npm run build
   - Fix any build errors
   - Check bundle size
```


### **Task 13.2: Deploy to Vercel (1 hour)**

**Steps:**

```bash
1. Create Vercel account (vercel.com)

2. Import project:
   - Click "New Project"
   - Import my3-frontend from GitHub
   - Vercel auto-detects Next.js

3. Configure:
   - Framework: Next.js
   - Root directory: /
   - Build command: npm run build
   - Output directory: .next

4. Set environment variables:
   - NEXT_PUBLIC_API_URL=https://my3-backend.railway.app
   - NEXTAUTH_URL=https://my3.vercel.app
   - NEXTAUTH_SECRET=your-secret

5. Deploy:
   - Click "Deploy"
   - Vercel builds and deploys
   - Get URL: https://my3.vercel.app

6. Set up custom domain (optional):
   - Buy domain: my3.app
   - Add to Vercel project
   - Update DNS
   - Vercel handles SSL automatically
```


### **Task 13.3: Verify Production (1 hour)**

Test everything in production:

- [ ] Landing page loads
- [ ] Sign up works
- [ ] Login works
- [ ] Dashboard loads
- [ ] Chat works (LLM responds)
- [ ] Recipients added via chat
- [ ] Graph updates
- [ ] Mobile works
- [ ] Dark mode works

***

## **Day 33-34: Monitoring \& Analytics**

### **Task 14.1: Set Up Analytics (2 hours)**

**Option 1: Vercel Analytics (Easiest)**

```bash
npm install @vercel/analytics
```

Add to `app/layout.tsx`:

```typescript
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

**Option 2: PostHog (More features)**

- Sign up at posthog.com
- Add tracking code
- Track events: sign_up, gift_search, recipient_added


### **Task 14.2: Error Monitoring (1 hour)**

**Add simple error tracking:**

Create `lib/logger.ts`:

```typescript
export const logError = async (error: Error, context?: any) => {
  console.error('Error:', error, context);
  
  // Send to backend for logging
  if (process.env.NODE_ENV === 'production') {
    await fetch('/api/log-error', {
      method: 'POST',
      body: JSON.stringify({
        message: error.message,
        stack: error.stack,
        context
      })
    });
  }
};
```

Use in error boundaries and catch blocks.

### **Task 14.3: Backend Logging (1 hour)**

**Cursor Prompt** (update `app/main.py`):

```
Add structured logging:

import logging
import json
from datetime import datetime

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
        }
        return json.dumps(log_data)

# Add middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info({
        'path': request.url.path,
        'method': request.method,
        'status': response.status_code,
        'duration': duration
    })
    
    return response

# Log LLM calls
# Log errors
# Log user actions
```


***

## **Day 35-36: Beta Testing**

### **Task 15.1: Invite Beta Users (2 hours)**

Create invite list:

1. Friends/family (5-10 people)
2. Share on Twitter/LinkedIn
3. Post in relevant communities

Create feedback form:

- Google Form or Typeform
- Questions:
    - What did you like?
    - What was confusing?
    - What features are missing?
    - Would you pay for this?
    - How much? (\$5, \$10, \$20/mo)


### **Task 15.2: Monitor Usage (Ongoing)**

Watch for:

- Sign-up conversion rate
- Daily active users
- Messages per user
- Recipients added per user
- Errors/crashes
- Performance issues


### **Task 15.3: Fix Critical Issues (2 hours)**

Based on feedback:

- Fix blocking bugs
- Improve confusing UX
- Add missing features (quick wins)

***

## **Day 37-38: Polish \& Final Touches**

### **Task 16.1: SEO Optimization (1 hour)**

**Cursor Prompt** (update `app/layout.tsx`):

```
Add SEO metadata:

export const metadata: Metadata = {
  title: 'My3 - Your AI Gift Concierge',
  description: 'Never forget a birthday again. AI-powered gift recommendations for the people who matter most.',
  keywords: ['gift ideas', 'birthday reminder', 'AI assistant', 'gift concierge'],
  openGraph: {
    title: 'My3 - Your AI Gift Concierge',
    description: 'Never forget a birthday again.',
    url: 'https://my3.vercel.app',
    siteName: 'My3',
    images: [
      {
        url: 'https://my3.vercel.app/og-image.png',
        width: 1200,
        height: 630,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My3 - Your AI Gift Concierge',
    description: 'Never forget a birthday again.',
    images: ['https://my3.vercel.app/og-image.png'],
  },
};
```

Create OG image (1200x630px) with Figma/Canva.

### **Task 16.2: Performance Final Check (1 hour)**

Run audits:

```bash
npm run build
npm run start

# Lighthouse audit
# Target: 90+ scores across the board

# Fix any issues:
- Unused CSS
- Large images
- Blocking scripts
- Missing alt tags
```


### **Task 16.3: Legal Pages (1 hour)**

Create basic pages:

- Privacy Policy (`app/privacy/page.tsx`)
- Terms of Service (`app/terms/page.tsx`)

Use templates:

- getterms.io
- termly.io

Covers:

- Data collection
- OpenAI usage
- User responsibilities
- Service changes

***

## **Day 39-42: Buffer \& Contingency**

Use this time for:

- Unexpected bugs
- Performance tuning
- Additional feedback implementation
- Documentation improvements

***

# **WHAT ELSE YOU NEED**

## **Post-Launch Essentials**

### **1. Pricing Strategy (If you want to monetize)**

```
Free Tier:
- Up to 10 relationships
- 50 messages/month
- Basic gift suggestions

Pro Tier ($9.99/mo):
- Unlimited relationships
- Unlimited messages
- Priority support
- Export data
- Advanced analytics
```


### **2. Support System**

- Email: support@my3.app
- FAQ page
- In-app chat widget (Intercom/Crisp)


### **3. Marketing**

- Product Hunt launch
- Twitter announcement
- LinkedIn post
- Reddit (r/SideProject)
- Indie Hackers


### **4. Backup Strategy**

- Database backups (Railway auto-backups)
- Code backups (GitHub)
- Disaster recovery plan


### **5. Legal**

- Privacy policy ✅ (Task 16.3)
- Terms of service ✅ (Task 16.3)
- Cookie consent (if EU users)
- GDPR compliance (if needed)


### **6. Future Features (Post-MVP)**

- Gift budget tracking
- Photo uploads for recipients
- Shared networks (families)
- Gift history timeline
- Recurring reminders
- Integration with Amazon API
- Mobile app (React Native)
- Voice input (Web Speech API)
- Multi-language support

***

# **COMPLETE SPRINT SUMMARY**

## **Timeline: 6 Weeks**

| Sprint | Duration | Key Deliverables |
| :-- | :-- | :-- |
| **Sprint 0** | Day 1 | Project setup |
| **Sprint 1** | Weeks 1-2 | Core agent + chat interface |
| **Sprint 2** | Weeks 3-4 | Polish + smart features |
| **Sprint 3** | Weeks 5-6 | Deployment + launch |

## **Final Checklist**

- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] Custom domain configured (optional)
- [ ] Analytics installed
- [ ] Error monitoring active
- [ ] Beta users invited
- [ ] Legal pages created
- [ ] SEO optimized
- [ ] Performance > 90 Lighthouse score
- [ ] Mobile fully functional
- [ ] Dark mode working
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Backup strategy in place
- [ ] Support email set up

***

# **YOU'RE READY TO SHIP! 🚀**

That's the complete sprint plan. You now have:

1. ✅ Full backend with LangGraph
2. ✅ Beautiful conversation-first frontend
3. ✅ Network graph background design
4. ✅ Deployment strategy
5. ✅ Monitoring \& analytics
6. ✅ Launch plan

** Want to create the landing page and dashboard page similar to that of https://www.microsoft.com/en-us/edge/update/year-in-review?form=MT016U&channel=stable&version=143.0.3650.96&sg=0&cs=839917877 **

## BACKLOG

### Animated Background Issue (Dec 30, 2025)
- **Status**: Not Working
- **Component**: `AnimatedBackground.tsx`
- **Issue**: Particles not rendering on dashboard page
- **Attempted Fixes**:
  - Updated to @tsparticles/react v3
  - Added loadLinksInteraction and loadExternalConnectInteraction plugins
  - Added error handling and fallback gradient
  - Added debug logging
- **Next Steps**: 
  - Investigate why particles aren't initializing
  - Check browser console for errors
  - Consider alternative approach (CSS animations, Three.js, or simpler particle library)
  - Test with minimal configuration first

### Recurring Date Management (Dec 30, 2025)
- **Status**: Known Limitation
- **Issue**: Birthdays and anniversaries stored with specific year need annual refresh
- **Current Behavior**: 
  - Dates are stored as upcoming dates (current year or next year)
  - After the date passes, it becomes a "past" date and won't automatically recur
- **Impact**: 
  - System needs to refresh recurring dates annually to keep them "upcoming"
  - Reminders may not work correctly after the first year
- **Next Steps**:
  - Consider storing dates as month/day only (requires schema change)
  - Implement annual date refresh job/cron task
  - Or use a recurring event system that calculates upcoming dates dynamically

### Historical Date Accuracy (Dec 30, 2025)
- **Status**: Known Limitation
- **Issue**: Stored dates may not reflect actual historical dates for calculations
- **Current Behavior**: 
  - For recurring events without year, system stores upcoming date (current/next year)
  - This date is used for all queries, including historical calculations
- **Impact**: 
  - Questions like "How many years since they are married?" may be inaccurate
  - System uses the stored "upcoming" date instead of actual historical date
- **Next Steps**:
  - Separate "historical_date" field for actual event date
  - Or prompt user for actual year when adding birthdays/anniversaries
  - Store both "event_date" (historical) and "next_occurrence" (upcoming) dates

### Sprint 2 Remaining Items (Post-Deployment)
- **Status**: Deferred to Post-Deployment
- **Items**:
  - **Dark Mode**: Fully implement dark mode toggle and theme switching (2-3 hours)
  - **Enhanced Graph Tooltips**: Rich tooltips with occasion countdown and gift history (2 hours)
  - **Node Animations**: Urgency pulse, entrance animations, hover states (2 hours)
  - **Proactive Reminders**: 30-day occasion reminders system (3-4 hours)
  - **Auto-Update Intelligence**: Enhanced agent logic for auto-updating recipient info (3 hours)
  - **Context Injection**: Reminder injection into chat context (1 hour)
  - **Graph Empty State**: Beautiful empty state with ghost nodes (1 hour)
  - **Landing Page Enhancements**: Footer, navigation header, demo chat improvements (2-3 hours)
  - **Performance Optimization**: Bundle size, lazy loading, caching (2 hours)

### Pre-Deployment Critical Items (Completed Jan 1, 2025)
- **Status**: ✅ Completed
- **Items Completed**:
  - ✅ **Error Handling & User Feedback**: Enhanced error messages, error boundaries, retry functionality, specific error handling for different scenarios
  - ✅ **Loading States & Skeletons**: Added skeleton loaders, loading indicators, disabled states, "My3 is typing" animation
  - ✅ **Mobile Responsiveness**: Verified and improved mobile layout for chat window, forms, and responsive breakpoints
  - ✅ **Basic SEO Metadata**: Added Open Graph tags, Twitter cards, structured data (JSON-LD), and comprehensive metadata

