# GovFunding Chatbot

**AI-powered federal grant discovery** – Find funding 10× faster through conversational search.

GovFunding Chatbot is an AI-native research funding assistant that aggregates NSF and Grants.gov opportunities, powers a GPT-4-driven conversational interface, and provides intelligent grant recommendations. Unlike traditional grant databases (GrantForward, GrantWatch) that require complex filtering, we offer a ChatGPT-like experience: ask questions, get personalized answers with citations.

**Live Demo**: [govfundingchatbot.vercel.app](https://govfundingchatbot.vercel.app)

## 🚀 Quick Start

### Try the Live App
Visit [govfundingchatbot.vercel.app](https://govfundingchatbot.vercel.app) and click the chat button to:
- Ask: "What are the latest NSF opportunities?"
- Find grants for your research area in seconds
- Get AI-powered recommendations with citations

### Run Locally

#### Web Application (Next.js)
```bash
cd apps/web
npm install
cp .env.sample .env  # Add Supabase + OpenAI credentials
npm run dev          # Open http://localhost:3000
```

#### ETL Pipeline (Python)
```bash
poetry install
cp .env.sample .env  # Add NSF API + Grants.gov URLs
scripts/run_etl.sh   # Populates Supabase with grant data
```

**Required Environment Variables**:
- `OPENAI_API_KEY` – For conversational AI (GPT-4 + embeddings)
- `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY` – Grant database
- `NSF_API_KEY` + `GRANTS_GOV_XML_URL` – Data sources (ETL only)

## ✨ Key Features

### 🤖 Conversational AI (v1.1.1)
- **Floating Chat Button**: Ask questions on any page, get instant AI answers
- **GPT-4 Powered**: Natural language understanding + retrieval-augmented generation (RAG)
- **Real-time Streaming**: See responses as they're generated (<800ms first token)
- **Chat History**: Dashboard widget saves last 10 conversations

### 🔍 Grant Discovery
- **Live Database**: NSF + Grants.gov opportunities updated daily via ETL
- **Smart Search**: Full-text + semantic search (Pinecone integration coming in v1.2.0)
- **Detailed Pages**: Award ranges, deadlines, eligibility, agency contacts

### 📊 Dashboard & Analytics
- **Active Opportunities**: Real-time count of open grants
- **Funding Metrics**: Total available funding across agencies
- **Chat Analytics**: Review past conversations and recommendations

## 📁 Repository Structure

```
govfundingchatbot/
├── apps/
│   ├── etl/              # Python ETL pipeline (NSF + Grants.gov → Supabase)
│   └── web/              # Next.js 14 app (conversational UI + dashboard)
│       ├── app/          # Pages (landing, dashboard, search, opportunities)
│       ├── components/   # FloatingChat, ChatHistory, UI primitives
│       └── api/chat/     # GPT-4 streaming endpoint with RAG
├── docs/
│   ├── product/          # Roadmap, user research, data pipeline specs
│   ├── architecture/     # System diagrams, service plans
│   └── releases/         # Comprehensive release notes (v1.0.0+)
├── release-notes/        # Detailed changelogs (v1.0.0 → v1.1.1)
├── scripts/              # run_etl.sh (automated data pipeline)
└── CLAUDE.md             # AI assistant context & project guide
```

## 🗺️ Roadmap

See [docs/product/roadmap.md](docs/product/roadmap.md) and [release-notes/v2.0.0-STRATEGIC_PLAN.md](release-notes/v2.0.0-STRATEGIC_PLAN.md) for complete vision.

### ✅ Completed
- **v1.0.0** (Oct 2025): ETL pipeline, Supabase integration, foundational architecture
- **v1.1.0** (Oct 2025): Repository restructure, documentation overhaul
- **v1.1.1** (Oct 2025): **Conversational AI interface, chat history, GPT-4 streaming**

### 🔄 In Progress (v1.2.0 - Nov 2025)
- Pinecone vector search (semantic matching)
- Rate limiting & abuse prevention
- User feedback widget (thumbs up/down)
- Citation links in AI responses

### 📅 Planned (v1.3.0 - Q1 2026)
- User authentication (Supabase Auth)
- Cross-device chat sync (server-side storage)
- Proactive AI alerts (email/Slack notifications)
- Application assistance (concept note generator, eligibility checker)

### 🎯 Long-term Vision
- Freemium pricing ($0-49/mo vs. competitors' $39-10K)
- Institutional accounts with API access
- AI-powered proposal drafting
- Success rate analytics

## 📦 Release History

| Version | Date | Highlights |
|---------|------|------------|
| **v1.1.1** | Oct 10, 2025 | 🤖 Conversational AI, floating chat, dashboard history |
| **v1.1.0** | Oct 10, 2025 | 📁 Repository restructure, agent documentation |
| **v1.0.0** | Oct 10, 2025 | 🏗️ ETL pipeline, Supabase integration, foundation |

**Full Release Notes**: See [release-notes/](release-notes/) for detailed changelogs, migration guides, and technical specs.

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork & Clone**: Fork this repo and clone locally
2. **Setup Environment**:
   ```bash
   # Web app
   cd apps/web && npm install

   # ETL pipeline
   poetry install
   ```
3. **Create Branch**: `git checkout -b feature/your-feature-name`
4. **Make Changes**: Follow existing patterns in codebase
5. **Test Locally**:
   - Web: `npm run dev` (check http://localhost:3000)
   - ETL: `scripts/run_etl.sh` (verify Supabase updates)
6. **Update Docs**: Add to `release-notes/` if significant change
7. **Submit PR**: Describe what you built and why

**Code Standards**:
- Python: `ruff` + `black` formatting
- TypeScript: `eslint` + `prettier` (configured in `apps/web`)
- Commit messages: Conventional commits (`feat:`, `fix:`, `docs:`)

**Questions?** Open a GitHub issue or check [CLAUDE.md](CLAUDE.md) for AI assistant context.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [OpenAI GPT-4](https://openai.com) – Conversational AI
- [Supabase](https://supabase.com) – Real-time database
- [Next.js](https://nextjs.org) – React framework
- [Vercel](https://vercel.com) – Deployment platform
- [Tailwind CSS](https://tailwindcss.com) – Styling

**Inspired by**: The need for accessible, AI-powered grant discovery that doesn't cost $5K-10K/year.

---

**⭐ Star this repo** if you find it useful! | **🐛 Report bugs** via [GitHub Issues](https://github.com/HosungYou/govfundingchatbot/issues) | **💬 Chat with the live app** at [govfundingchatbot.vercel.app](https://govfundingchatbot.vercel.app)
