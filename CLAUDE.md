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
