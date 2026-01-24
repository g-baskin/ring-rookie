# Ring Rookie

AI-powered voice agent platform for configuring and deploying custom voice agents with tool calling, multi-provider support, and transparent pricing tiers.

## Project Structure

```
ring-rookie/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── api/               # API routes (agents, auth, crm, realtime, telephony, workspaces)
│   │   ├── core/              # Config, security, auth, rate limiting
│   │   ├── db/                # Database session, Redis client
│   │   ├── middleware/        # Request tracing, security headers
│   │   ├── models/            # SQLAlchemy models (user, agent, contact, appointment, workspace)
│   │   └── services/          # Business logic & integrations
│   │       └── tools/         # Voice agent tools (CRM, SMS, calendars)
│   ├── migrations/versions/   # Alembic database migrations
│   └── tests/                 # Backend tests (unit, integration, api)
├── frontend/                   # Next.js 15 React frontend
│   ├── src/
│   │   ├── app/dashboard/     # Dashboard pages (agents, crm, calls, settings, workspaces)
│   │   ├── app/embed/         # Embeddable voice widget
│   │   ├── components/ui/     # shadcn/ui components
│   │   ├── hooks/             # Custom React hooks
│   │   └── lib/api/           # API client functions
│   └── public/                # Static assets
└── docker-compose.yml         # PostgreSQL 17 + Redis 7
```

## Organization Rules

**Backend:**
- API routes → `app/api/`, one file per resource
- Business logic → `app/services/`, organized by domain
- Models → `app/models/`, one model per file
- Tools → `app/services/tools/`, one class per integration

**Frontend:**
- Pages → `src/app/dashboard/`, using Next.js App Router
- Components → `src/components/`, reusable UI elements
- Lib → `src/lib/`, utilities, types, API clients
- One component per file, co-locate related files

## Code Quality - Zero Tolerance

### Backend:
```bash
cd backend
uv run ruff check app tests --fix        # Lint + auto-fix
uv run ruff format app tests             # Format
uv run mypy app                          # Type check (strict)
```

### Frontend:
```bash
cd frontend
npm run check                            # eslint + tsc + prettier
npm run lint:fix && npm run format       # Auto-fix
```

### Server Checks:
```bash
cd backend && uv run uvicorn app.main:app --reload   # Check runtime warnings
cd frontend && npm run dev                            # Check compilation warnings
```

**Fix ALL errors/warnings before continuing!**

## Key Commands

- `/update-app` - Update dependencies, fix deprecations
- `/check` - Run all quality checks, auto-fix issues
- `/commit` - Run checks, commit with AI message, push

## Tech Stack

**Voice & AI**: Pipecat, Deepgram, ElevenLabs, OpenAI GPT-4o Realtime
**Backend**: FastAPI, PostgreSQL 17, Redis 7, SQLAlchemy 2.0, Python 3.12+, uv
**Frontend**: Next.js 15, React 19, TypeScript 5.7, Tailwind, shadcn/ui
**Telephony**: Telnyx (primary), Twilio (optional)

## Important Patterns

### User ID Mapping (Integer ↔ UUID)

The codebase has two user ID formats that must be converted:

| Table | Column | Type | Example |
|-------|--------|------|---------|
| `users` | `id` | Integer | `1` |
| `agents` | `user_id` | Integer | `1` |
| `user_settings` | `user_id` | UUID | `43f2e40a-0efc-559a-8a82-981306f42751` |
| `call_records` | `user_id` | UUID | `43f2e40a-0efc-559a-8a82-981306f42751` |

**Always use `user_id_to_uuid()` when:**
- Looking up `user_settings` from an agent's `user_id`
- Creating `call_records` from an agent's `user_id`
- Any operation requiring UUID user_id from integer user_id

```python
from app.core.auth import user_id_to_uuid

# Convert integer user_id to UUID
user_uuid = user_id_to_uuid(agent.user_id)  # 1 → 43f2e40a-0efc-559a-8a82-981306f42751
```

The function uses UUID5 with a fixed namespace for deterministic, consistent conversion.

### Embed Widget Origin Validation

The embed API validates Origin headers for security. Special cases:

- **Null origins**: Allowed when `localhost` is in `allowed_domains` (for same-origin iframe requests)
- **Wildcards**: `*.example.com` matches any subdomain
- **Empty list**: Allows all origins (dev/testing only)

## Data Seeding (Dev → QA → Prod)

Database schema changes follow CI/CD via Alembic migrations. **Data** (agents, users, settings) requires explicit seeding.

### Seed Script Location
```
backend/
├── scripts/seed_data.py    # Seed management CLI
└── seeds/                   # JSON seed files (git-tracked)
    └── mragame_agent.json  # Example: MrAGame voice agent
```

### Commands

```bash
cd backend && source .venv/bin/activate

# List agents in an environment
python scripts/seed_data.py list --env local
python scripts/seed_data.py list --env production

# Export agent to seed file (strips secrets with --no-secrets)
python scripts/seed_data.py export --env local --agent ag_IXqnWYBG -o seeds/my_agent.json
python scripts/seed_data.py export --env local --agent ag_IXqnWYBG -o seeds/my_agent.json --no-secrets

# Import seed file to environment
python scripts/seed_data.py import --env production -i seeds/my_agent.json
python scripts/seed_data.py import --env production -i seeds/my_agent.json --no-secrets

# Direct sync between environments
python scripts/seed_data.py sync --source local --target production --agent ag_IXqnWYBG
```

### Docker Support

The script auto-detects Docker environments and uses appropriate hostnames:
- **Local (bare metal)**: `postgresql://postgres:postgres@localhost:5432/ringrookie`
- **Docker container**: `postgresql://postgres:postgres@db:5432/ringrookie`

Override with environment variables:
```bash
DATABASE_URL=postgresql://... python scripts/seed_data.py import -i seeds/agent.json
```

### CI/CD Integration

Add to your deployment workflow:

```yaml
# .github/workflows/deploy.yml
- name: Seed production data
  run: |
    cd backend
    pip install asyncpg
    python scripts/seed_data.py import --env production -i seeds/production_agents.json --no-secrets
  env:
    PROD_DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Security Notes

- **--no-secrets**: Strips API keys, passwords before export (safe for git)
- **Full export**: Contains encrypted passwords and API keys (keep secure)
- **Seed files in git**: Only commit `--no-secrets` versions
- **API keys in prod**: Add manually via dashboard or secure env vars

## Chat Champ Integration

**Chat Champ** is MrAGame's 6th product - an embeddable AI chat widget SaaS that shares backend infrastructure with Ring Rookie.

### What Chat Champ Provides

| Feature | Description |
|---------|-------------|
| **Streaming Responses** | Real-time token-by-token display via SSE |
| **Knowledge Base (RAG)** | Upload docs, PDFs, URLs for context-aware responses |
| **Conversation History** | Persist & search past conversations |
| **Custom Branding** | Colors, greeting, position customization |
| **Usage-Based Billing** | FREE (50 msg/day), PRO (2000), BUSINESS (10000), ENTERPRISE (unlimited) |

### Shared Infrastructure

Chat Champ reuses Ring Rookie's:
- **Tool registry** - CRM, Calendly, Shopify, SMS integrations
- **Agent model** - Extended with `greeting_message`, `embed_config`, RAG settings
- **Workspace multi-tenancy** - Same team/permission model
- **Public embed API** - `/api/public/chat/{public_id}/stream`

### Key Backend Models

```python
# Extended Agent fields (app/models/agent.py)
greeting_message: str           # Initial chat greeting
embed_config: dict              # Widget customization settings
rag_enabled: bool               # Enable knowledge base
knowledge_base_id: UUID         # Link to knowledge base

# Usage metering (app/models/usage.py)
UsageRecord                     # Daily message tracking
AgentBillingConfig              # Tier configuration per agent
BillingTier                     # FREE, PRO, BUSINESS, ENTERPRISE

# Knowledge base (app/models/knowledge.py)
KnowledgeBase                   # Document collection
KnowledgeDocument               # Uploaded files/URLs
KnowledgeChunk                  # Embedded text chunks (pgvector)
```

### API Endpoints

```
POST /api/public/chat/{public_id}/stream     # SSE streaming chat
GET  /api/public/chat/{public_id}/config     # Widget configuration
GET  /api/public/chat/{public_id}/history    # Conversation history
GET  /api/usage/agent/{id}/status            # Usage limits check
POST /api/knowledge/{kb_id}/upload           # Upload documents
POST /api/knowledge/{kb_id}/search           # Vector similarity search
```

### Embeddable Widget

One-line embed for any website:
```html
<script src="https://chat.mragame.com/widget.js" data-agent="ag_XXXXX"></script>
```

Widget source: `/projects/mragame/widget/chat-champ.ts` (11.4kb minified)

### Vector Embeddings

Uses pgvector with IVFFlat indexing:
- Model: OpenAI `text-embedding-3-small` (1536 dimensions)
- Similarity: Cosine distance
- Chunk size: 500 tokens with 50 token overlap
