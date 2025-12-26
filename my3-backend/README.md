# My3 Backend

FastAPI + LangGraph backend for My3 - AI-powered personal relationship and gifting concierge.

## Project Structure

```
my3-backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/              # API routes
│   │   ├── routes/       # Auth, chat, recipients endpoints
│   │   └── dependencies.py
│   ├── database/         # Database models, schemas, connection
│   ├── graph/            # LangGraph workflow
│   │   ├── state.py      # Workflow state definition
│   │   ├── nodes.py      # Workflow nodes
│   │   └── workflow.py    # Workflow compilation
│   ├── utils/            # Utilities (LLM, auth)
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
├── tests/                # Test files
├── docker-compose.yml    # PostgreSQL setup
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## Setup Instructions

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

4. **Start PostgreSQL:**
   ```bash
   docker-compose up -d
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `POST /api/chat` - Chat with My3 agent
- `POST /api/chat/confirm` - Confirm an action
- `GET /api/recipients` - Get all recipients
- `GET /api/recipients/{id}` - Get specific recipient
- `POST /api/recipients` - Create recipient (max 10 per user)
- `PUT /api/recipients/{id}` - Update recipient
- `DELETE /api/recipients/{id}` - Delete recipient
- `GET /api/health` - Health check

## Database Models

- **User**: User accounts
- **Recipient**: People user wants to gift (max 10 per user)
- **Occasion**: Gift occasions (birthdays, anniversaries, etc.)
- **GiftIdea**: Gift recommendations
- **Conversation**: Chat conversations
- **Message**: Individual chat messages

## LangGraph Workflow

The workflow consists of 6 nodes:
1. **greeting** - Initial greeting
2. **profiling** - Extract recipient/occasion info
3. **recommending** - Generate gift recommendations
4. **confirming** - Handle confirmations
5. **done** - Finalize conversation

## Development

- Run tests: `pytest`
- Create migration: `alembic revision --autogenerate -m "description"`
- Apply migration: `alembic upgrade head`

