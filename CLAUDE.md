# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the GovFunding Chatbot codebase.

---

## Repository Overview

**GovFunding Chatbot** is an AI-native federal grant discovery platform that helps researchers find funding opportunities through conversational search. Unlike traditional grant databases (GrantForward, GrantWatch) requiring complex filtering, we offer a ChatGPT-like experience powered by GPT-4 and retrieval-augmented generation (RAG).

**Live Demo**: [govfundingchatbot.vercel.app](https://govfundingchatbot.vercel.app)

**Current Version**: v1.1.1 (Conversational AI interface released Oct 10, 2025)

---

## Project Structure

```
govfundingchatbot/
├── apps/
│   ├── etl/                    # Python ETL pipeline
│   │   ├── sources/            # NSF Awards API, Grants.gov XML extractors
│   │   ├── transformers/       # Data normalization to unified schema
│   │   ├── writers/            # Supabase writers, local JSON snapshots
│   │   ├── embeddings/         # OpenAI embedding generation (Pinecone ready)
│   │   ├── config.py           # Settings (env vars, API keys)
│   │   └── pipeline.py         # Main entry point
│   │
│   └── web/                    # Next.js 14 application
│       ├── app/
│       │   ├── page.tsx        # Landing page
│       │   ├── dashboard/      # Main user dashboard + chat history
│       │   ├── search/         # Grant search with filters
│       │   ├── opportunities/[id]/  # Opportunity detail pages
│       │   └── api/chat/       # GPT-4 streaming endpoint (RAG)
│       │
│       └── components/
│           ├── FloatingChat.tsx     # Persistent chat button + panel
│           └── ChatHistory.tsx      # Dashboard conversation history widget
│
├── docs/
│   ├── product/               # Roadmap, UI specs, user research
│   ├── architecture/          # System diagrams, service plans
│   └── releases/              # Archived comprehensive release notes
│
├── release-notes/             # Versioned changelogs (v1.0.0+)
├── scripts/                   # run_etl.sh (automated data pipeline)
└── PROJECT_STRUCTURE.md       # Detailed repo layout documentation
```

---

## Technology Stack

### Frontend (apps/web)
- **Framework**: Next.js 14 with App Router (React Server Components)
- **Styling**: Tailwind CSS (utility-first, responsive)
- **State Management**: React hooks (useState, useEffect) + localStorage for chat persistence
- **AI Integration**: OpenAI GPT-4 streaming via `/api/chat` Edge function
- **Database**: Supabase (PostgreSQL) for grant data, full-text search
- **Deployment**: Vercel (Edge Runtime for <200ms cold starts)

### Backend (apps/etl)
- **Language**: Python 3.10+
- **Package Manager**: Poetry (dependency management)
- **Data Sources**:
  - NSF Awards API (REST)
  - Grants.gov XML snapshot
- **Storage**:
  - Supabase (PostgreSQL) – production grant database
  - Local JSON – development snapshots
- **Embeddings**: OpenAI text-embedding-ada-002 (for future Pinecone integration)
- **Orchestration**: Shell scripts (`scripts/run_etl.sh`)

### AI & Search
- **Conversational AI**: OpenAI GPT-4 (streaming responses)
- **RAG (Current)**: Supabase full-text search (pg_trgm, websearch config)
- **RAG (Planned v1.2.0)**: Pinecone vector database (1536-dim embeddings)
- **Prompt Engineering**: System prompts in `/api/chat/route.ts`

---

## Development Workflow

### Setup Environment

#### Web Application
```bash
cd apps/web
npm install

# Configure environment
cp .env.sample .env
# Add:
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY
# - SUPABASE_SERVICE_ROLE_KEY (for API routes)
# - OPENAI_API_KEY

# Run dev server
npm run dev  # http://localhost:3000
```

#### ETL Pipeline
```bash
# Install Poetry
pipx install poetry

# Install dependencies
poetry install

# Configure environment
cp .env.sample .env
# Add:
# - NSF_API_KEY (optional, rate limits without)
# - GRANTS_GOV_XML_URL (snapshot URL)
# - NEXT_PUBLIC_SUPABASE_URL
# - SUPABASE_SERVICE_ROLE_KEY
# - OPENAI_API_KEY (for embeddings)
# - PINECONE_API_KEY (optional, for v1.2.0+)

# Run pipeline
scripts/run_etl.sh
# Or directly:
poetry run python -m apps.etl.pipeline
```

### Common Commands

#### Web Development
```bash
cd apps/web

npm run dev          # Start dev server
npm run build        # Production build (TypeScript check)
npm run lint         # ESLint + Prettier
npm run type-check   # TypeScript validation
```

#### ETL Operations
```bash
# Run full pipeline (fetch + transform + write)
scripts/run_etl.sh

# Run with specific date (for backfills)
scripts/run_etl.sh --date 2025-10-01

# Debug mode (verbose logging)
PYTHONPATH=. python -m apps.etl.pipeline --verbose
```

#### Database Operations
```bash
# Connect to Supabase
psql $NEXT_PUBLIC_SUPABASE_URL

# Check opportunity count
SELECT COUNT(*) FROM funding_opportunities WHERE deadline_status = 'open';

# View recent opportunities
SELECT opportunity_id, title, agency_name, close_date
FROM funding_opportunities
ORDER BY post_date DESC
LIMIT 10;
```

---

## Architecture Patterns

### Conversational AI Flow (v1.1.1)

```
User clicks floating chat button
  ↓
Enter question: "Find grants for AI research"
  ↓
POST /api/chat with messages array
  ↓
1. Generate embedding (OpenAI text-embedding-ada-002)
2. Search Supabase for relevant grants (full-text search)
3. Build context from top 5 opportunities
4. Stream GPT-4 completion with RAG context
  ↓
Receive streaming response (chunk-by-chunk)
  ↓
Auto-save to localStorage (chat_sessions)
  ↓
Display in ChatHistory widget on dashboard
```

**Key Files**:
- `apps/web/components/FloatingChat.tsx` – Client-side chat UI
- `apps/web/app/api/chat/route.ts` – Server-side RAG + GPT-4
- `apps/web/components/ChatHistory.tsx` – Dashboard widget

### ETL Data Flow

```
Scheduled cron (daily) OR manual trigger
  ↓
scripts/run_etl.sh
  ↓
1. Extract
   - NSFAwardsExtractor: Fetch recent awards from API
   - GrantsXMLExtractor: Download Grants.gov XML snapshot
  ↓
2. Transform
   - AwardTransformer: Normalize to unified Award schema
   - OpportunityTransformer: Normalize to Opportunity schema
  ↓
3. Load
   - SupabaseWriter: Upsert to funding_opportunities table
   - LocalWriter: Save JSON snapshots (data/ directory)
  ↓
4. Embeddings (if OPENAI_API_KEY configured)
   - OpportunityEmbedder: Generate embeddings for Pinecone
  ↓
Data available in Supabase → Powers web app search & RAG
```

**Key Files**:
- `apps/etl/pipeline.py` – Main orchestrator
- `apps/etl/sources/*.py` – API/XML extractors
- `apps/etl/transformers/*.py` – Data normalization
- `apps/etl/writers/supabase_writer.py` – Database integration

### RAG Context Retrieval (Current)

```typescript
// apps/web/app/api/chat/route.ts

// 1. User question → embedding
const embedding = await openai.embeddings.create({
  model: 'text-embedding-ada-002',
  input: lastMessage.content
})

// 2. Supabase full-text search (fallback until Pinecone integration)
const { data: opportunities } = await supabase
  .from('funding_opportunities')
  .select('opportunity_id, title, agency_name, summary, close_date, award_floor, award_ceiling')
  .textSearch('title', lastMessage.content, { type: 'websearch' })
  .eq('deadline_status', 'open')
  .limit(5)

// 3. Build context for GPT-4
const context = opportunities.map(opp => `
**Title:** ${opp.title}
**Agency:** ${opp.agency_name}
**Summary:** ${opp.summary}
**Award Range:** $${opp.award_floor}K - $${opp.award_ceiling}K
**Deadline:** ${opp.close_date}
`).join('\n---\n')

// 4. Inject into system prompt
const completion = await openai.chat.completions.create({
  model: 'gpt-4',
  stream: true,
  messages: [
    { role: 'system', content: `You are a grant expert. Use ONLY these opportunities:\n\n${context}` },
    ...userMessages
  ]
})
```

---

## Key Features & Implementation

### 1. Floating Chat Interface (v1.1.1)

**Component**: `apps/web/components/FloatingChat.tsx`

**Features**:
- Persistent across all pages (added to `app/layout.tsx`)
- Real-time streaming (ReadableStream API, not `ai` package due to OpenAI SDK v4 compatibility)
- Session management (auto-save to localStorage, max 10 sessions)
- Conversation starters for new users
- Error handling with user-friendly messages

**Storage Schema** (localStorage):
```typescript
interface ChatSession {
  id: string              // "session_1728576000000"
  title: string           // First message preview (50 chars)
  messages: Message[]     // Full conversation thread
  createdAt: number       // Unix timestamp
  updatedAt: number       // Unix timestamp
}

interface Message {
  id: string              // "msg_1728576123000"
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}
```

**Usage**:
```tsx
// Already integrated globally in apps/web/app/layout.tsx
import FloatingChat from '@/components/FloatingChat'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <FloatingChat />  {/* Available on all pages */}
      </body>
    </html>
  )
}
```

### 2. Dashboard Chat History

**Component**: `apps/web/components/ChatHistory.tsx`

**Features**:
- Real-time updates (storage events + 2s polling)
- Expandable conversation threads
- Delete functionality
- Empty state with onboarding

**Integration**:
```tsx
// apps/web/app/dashboard/page.tsx
import ChatHistory from '@/components/ChatHistory'

export default async function Dashboard() {
  // ... Supabase queries for opportunities ...

  return (
    <div>
      <h1>Dashboard</h1>

      {/* Chat History Section */}
      <ChatHistory />

      {/* Recent Opportunities */}
      {/* ... */}
    </div>
  )
}
```

### 3. RAG Endpoint

**Route**: `apps/web/app/api/chat/route.ts`

**Edge Runtime Configuration**:
```typescript
export const runtime = 'edge'  // Vercel Edge for low latency
```

**Error Handling**:
- Fallback to recent opportunities if search returns no results
- Graceful degradation if OpenAI API fails
- User-friendly error messages (not stack traces)

**Cost Optimization**:
- Stream responses (reduce perceived latency, same token cost)
- Limit context to top 5 opportunities (reduce input tokens)
- Use text-embedding-ada-002 (cheaper than GPT-4 embeddings)

---

## Environment Variables

### Required for Web App

```bash
# Supabase (Grant Database)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # For API routes

# OpenAI (Conversational AI)
OPENAI_API_KEY=sk-...  # For GPT-4 chat + embeddings
```

### Required for ETL Pipeline

```bash
# Data Sources
NSF_API_KEY=...  # Optional (higher rate limits with key)
GRANTS_GOV_XML_URL=https://...  # Pre-authenticated XML snapshot URL

# Database
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Embeddings (Optional, for Pinecone v1.2.0+)
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX=govfunding-opportunities
```

**Security Notes**:
- Never commit `.env` files (already in `.gitignore`)
- Use Vercel environment variables UI for production
- Rotate keys if accidentally exposed

---

## Testing & Quality Assurance

### Manual Testing Checklist

#### Chat Feature
- [ ] Floating button visible on all pages
- [ ] Chat opens/closes smoothly
- [ ] Streaming responses work correctly
- [ ] Messages save to localStorage
- [ ] Chat history appears on dashboard
- [ ] Delete conversation works
- [ ] Conversation starters insert correctly

#### Dashboard
- [ ] Stats display accurate counts
- [ ] Opportunity cards render with correct data
- [ ] Links to opportunity detail pages work
- [ ] Chat history updates in real-time

#### Search
- [ ] Keyword search returns relevant results
- [ ] Agency filter works
- [ ] Status filter (open/closed) works
- [ ] Empty state displays when no results

#### ETL Pipeline
- [ ] NSF API extraction completes without errors
- [ ] Grants.gov XML parsing succeeds
- [ ] Supabase upsert inserts/updates correctly
- [ ] Local JSON snapshots created
- [ ] Embedding generation works (if configured)

### Automated Testing (Planned v1.2.0)

```bash
# Web app tests
cd apps/web
npm run test        # Jest + React Testing Library
npm run test:e2e    # Playwright end-to-end tests

# ETL tests
poetry run pytest apps/etl/tests/
```

---

## Deployment

### Vercel (Web App)

**Automatic Deployment**:
- Connected to GitHub repo
- Auto-deploys on push to `main` branch
- Preview deployments for pull requests

**Manual Deployment**:
```bash
cd apps/web
npm run build       # Verify build succeeds
vercel --prod       # Deploy to production
```

**Environment Variables**:
- Configure in Vercel dashboard → Settings → Environment Variables
- Separate variables for Production/Preview/Development

**Monitoring**:
- Vercel Analytics (page views, performance)
- Vercel Logs (function errors, build logs)
- OpenAI Usage Dashboard (API costs)

### ETL Pipeline

**Scheduled Execution** (Recommended):
- GitHub Actions cron job (daily at 2 AM UTC)
- Render.com cron job (alternative)
- Manual trigger via `scripts/run_etl.sh`

**Example GitHub Action**:
```yaml
# .github/workflows/etl.yml
name: Daily ETL
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
  workflow_dispatch:     # Manual trigger

jobs:
  run-etl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pipx install poetry
      - run: poetry install
      - run: scripts/run_etl.sh
        env:
          NSF_API_KEY: ${{ secrets.NSF_API_KEY }}
          GRANTS_GOV_XML_URL: ${{ secrets.GRANTS_GOV_XML_URL }}
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
```

---

## Common Issues & Solutions

### Build Errors

**Issue**: TypeScript error in `/api/chat/route.ts` – `Stream<ChatCompletionChunk> is not assignable`

**Solution**: Use native `ReadableStream` instead of `OpenAIStream` from `ai` package (fixed in v1.1.1):
```typescript
// ❌ Old (broken with OpenAI SDK v4)
const stream = OpenAIStream(response)
return new StreamingTextResponse(stream)

// ✅ New (v1.1.1)
const stream = new ReadableStream({
  async start(controller) {
    const encoder = new TextEncoder()
    for await (const chunk of completion) {
      const content = chunk.choices[0]?.delta?.content || ''
      if (content) controller.enqueue(encoder.encode(content))
    }
    controller.close()
  }
})
return new Response(stream)
```

### ETL Failures

**Issue**: Grants.gov XML download fails with 403 Forbidden

**Solution**: Ensure `GRANTS_GOV_XML_URL` includes authentication token (pre-authenticated URL)

**Issue**: Supabase upsert fails with "relation does not exist"

**Solution**: Run database migrations first:
```sql
-- Create funding_opportunities table
CREATE TABLE funding_opportunities (
  opportunity_id TEXT PRIMARY KEY,
  title TEXT,
  agency_name TEXT,
  close_date TIMESTAMP,
  award_floor NUMERIC,
  award_ceiling NUMERIC,
  deadline_status TEXT,
  summary TEXT,
  post_date TIMESTAMP,
  -- ... additional fields ...
);

-- Enable full-text search
CREATE INDEX idx_fts_title ON funding_opportunities USING gin(to_tsvector('english', title));
```

### Chat Issues

**Issue**: Chat history not syncing across tabs

**Solution**: This is expected behavior (localStorage is tab-scoped). Server-side storage planned for v1.3.0.

**Issue**: AI responses are empty or cut off

**Solution**: Check OpenAI API quota/rate limits. Verify `OPENAI_API_KEY` is valid.

---

## Release Process

### Version Numbering
- **Major** (X.0.0): Breaking changes, new database schema
- **Minor** (1.X.0): New features, backward-compatible
- **Patch** (1.1.X): Bug fixes only

### Creating a Release

1. **Update Code & Docs**:
   ```bash
   # Make changes
   git add .
   git commit -m "feat: add new feature"
   ```

2. **Write Release Notes**:
   ```bash
   # Create release note following existing format
   # See release-notes/v1.1.1.md for template
   touch release-notes/v1.X.X.md
   ```

3. **Update README**:
   ```bash
   # Add version to release history table
   # Update feature list if applicable
   ```

4. **Tag Release**:
   ```bash
   git tag v1.X.X
   git push origin main --tags
   ```

5. **Deploy**:
   - Web: Vercel auto-deploys on tag push
   - ETL: Update GitHub Actions workflow if needed

6. **Announce**:
   - GitHub Releases (copy highlights from release notes)
   - User communication (if applicable)

---

## Roadmap Context

### Completed (v1.0.0 → v1.1.1)
- ✅ ETL pipeline with Supabase integration
- ✅ Next.js dashboard with live data
- ✅ Conversational AI interface (GPT-4 streaming)
- ✅ Chat history widget
- ✅ Search & filter pages

### In Progress (v1.2.0 - Nov 2025)
- 🔄 Pinecone vector search (semantic matching)
- 🔄 Rate limiting middleware
- 🔄 User feedback widget
- 🔄 Citation links in AI responses

### Planned (v1.3.0 - Q1 2026)
- 📅 User authentication (Supabase Auth)
- 📅 Server-side chat storage (cross-device sync)
- 📅 Proactive AI alerts (email/Slack)
- 📅 Application assistance (concept note generator)

### Long-term Vision (v2.0.0+)
- 🎯 Freemium pricing model ($0-49/mo)
- 🎯 Institutional accounts
- 🎯 AI proposal drafting
- 🎯 Success rate analytics

**Full Vision**: See [release-notes/v2.0.0-STRATEGIC_PLAN.md](release-notes/v2.0.0-STRATEGIC_PLAN.md)

---

## Code Standards

### TypeScript (Web App)
```typescript
// Use explicit types
interface Props {
  title: string
  count: number
}

// Prefer async/await over .then()
const data = await fetch('/api/endpoint')

// Use Server Components by default (Next.js 14)
export default async function Page() { /* ... */ }
```

### Python (ETL)
```python
# Type hints required
def transform(data: List[Dict]) -> List[Opportunity]:
    pass

# Use Pydantic for validation
from pydantic import BaseModel, Field

class Opportunity(BaseModel):
    opportunity_id: str = Field(..., description="Unique ID")
    title: str
    agency_name: str
```

### Commit Messages
```
feat: add new feature
fix: resolve bug
docs: update documentation
refactor: restructure code
test: add tests
chore: update dependencies
```

---

## Support & Resources

### Documentation
- [Release Notes](release-notes/) – Detailed changelogs
- [Product Roadmap](docs/product/roadmap.md) – Strategic plan
- [Architecture Diagrams](docs/architecture/) – System design

### External Links
- [Live App](https://govfundingchatbot.vercel.app)
- [GitHub Repo](https://github.com/HosungYou/govfundingchatbot)
- [Supabase Dashboard](https://supabase.com/dashboard)
- [Vercel Dashboard](https://vercel.com/dashboard)

### Getting Help
- **GitHub Issues**: [github.com/HosungYou/govfundingchatbot/issues](https://github.com/HosungYou/govfundingchatbot/issues)
- **Questions**: Tag issues with `question` label
- **Bugs**: Tag with `bug` label, include reproduction steps

---

**Last Updated**: October 10, 2025 (v1.1.1 release)
**Maintained By**: GovFunding Core Team
