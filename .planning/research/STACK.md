# Technology Stack

**Project:** FraudFish - Autonomous Fraud Intelligence Agent
**Researched:** 2026-03-24

## Recommended Stack

### Backend Core

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python | 3.12+ | Runtime | TinyFish SDK is Python-first. FastAPI requires 3.10+. 3.12 gives best performance and typing support without bleeding-edge 3.13/3.14 risk. | HIGH |
| FastAPI | 0.135.2 | API framework | Native SSE support (added in recent versions with `EventSourceResponse`), async-first, Pydantic integration for structured responses, fastest Python framework for this use case. Official SSE tutorial exists. | HIGH |
| uvicorn | 0.42.0 | ASGI server | Standard FastAPI deployment server. Handles async connections needed for SSE streaming. | HIGH |
| sse-starlette | 3.3.3 | SSE implementation | W3C-compliant SSE for FastAPI. Handles keep-alive pings (15s default), `Cache-Control: no-cache`, `X-Accel-Buffering: no` automatically. Supports client disconnect detection and cooperative shutdown. | HIGH |
| Pydantic | 2.12+ | Data validation | Already a FastAPI dependency. Use for all data models: investigation signals, verdict schemas, OpenAI structured output definitions. v2 is 5-50x faster than v1. | HIGH |

### TinyFish Integration

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| TinyFish Python SDK | latest | Web agent API | Official SDK (`from tinyfish import TinyFish`). `client.agent.stream()` returns SSE events natively - perfect for piping investigation steps to the frontend in real-time. Natural language goals mean no CSS selectors or XPath to maintain. | HIGH |
| httpx | 0.28.1 | HTTP client (fallback) | If the TinyFish SDK has gaps or you need direct REST calls to `https://agent.tinyfish.ai/v1/automation/run-sse`, httpx provides async SSE streaming support. Also useful for any direct API calls to official ticket sites. | MEDIUM |

**TinyFish API Pattern:**
```python
from tinyfish import TinyFish, EventType

client = TinyFish()  # Uses TINYFISH_API_KEY env var

with client.agent.stream(
    url="https://www.carousell.sg/p/listing-id",
    goal="Extract seller name, price, description, transfer method, and account age",
) as stream:
    for event in stream:
        # Each event is an investigation step you can forward via SSE
        yield event
```

**Key TinyFish Parameters:**
- `url`: Target page
- `goal`: Natural language extraction/navigation instruction
- `browser_profile`: Use `BrowserProfile.STEALTH` for Carousell/Viagogo (anti-bot protected)
- `proxy_config`: Geographic routing (SG proxies for local marketplace access)

### AI Classification

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| openai | 2.29.0 | OpenAI API client | Hackathon sponsor, free credits provided. v2.x is current (v1.x deprecated). Use `client.chat.completions.parse()` with Pydantic models for guaranteed structured output. | HIGH |
| gpt-4o | latest | Classification model | Strong structured output support via `response_format=PydanticModel`. Fast enough for real-time classification. Handles nuanced fraud reasoning well. | HIGH |
| gpt-4o-mini | latest | Quick classification (fallback) | 10x cheaper, faster. Use for obvious cases or as fallback when gpt-4o is slow/rate-limited. | MEDIUM |

**Structured Output Pattern:**
```python
from pydantic import BaseModel
from openai import OpenAI

class FraudVerdict(BaseModel):
    category: Literal["LEGITIMATE", "SCALPING_VIOLATION", "LIKELY_SCAM", "COUNTERFEIT_RISK"]
    confidence: float
    reasoning: str
    signals: list[SignalAssessment]

client = OpenAI()
completion = client.chat.completions.parse(
    model="gpt-4o",
    messages=[...],
    response_format=FraudVerdict,
)
verdict = completion.choices[0].message.parsed  # Typed, validated Pydantic model
```

### Frontend Core

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| React | 19.2.x | UI framework | Industry standard, fast to build with. Hooks-based state management handles SSE event streams naturally. | HIGH |
| Vite | 8.0.x | Build tool / dev server | Vite 8 uses Rolldown (Rust-based), giving 5x faster builds. `npm create vite@latest -- --template react-ts`. Sub-second HMR during hackathon development. | HIGH |
| TypeScript | 5.x | Type safety | Catch errors at dev time. Type SSE event shapes to match backend Pydantic models. Non-negotiable for a project with complex data flow. | HIGH |
| Tailwind CSS | 4.2.x | Styling | Utility-first, zero config in v4 (CSS-native engine). Fastest way to build a polished UI in a hackathon. No component library overhead. | HIGH |

### Frontend Animation & UX

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| motion (formerly framer-motion) | 12.37.x | Animation | Signal-by-signal animated reveal is a core UX requirement. `motion` provides `AnimatePresence`, layout animations, and stagger effects. Import from `motion/react`. | HIGH |

**SSE Client Pattern (no library needed):**
```typescript
// Native EventSource - no npm package required
const eventSource = new EventSource(`/api/investigate?url=${encodeURIComponent(listingUrl)}`);

eventSource.onmessage = (event) => {
  const signal = JSON.parse(event.data);
  setSignals(prev => [...prev, signal]);  // Each signal triggers animated card reveal
};

eventSource.onerror = () => eventSource.close();
```

### Dev Tooling

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| uv | latest | Python package manager | 10-100x faster than pip. Single `uv pip install` replaces pip + venv setup. Critical for hackathon speed. | HIGH |
| ruff | latest | Python linter/formatter | Replaces flake8 + black + isort. Single tool, instant execution. | MEDIUM |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backend framework | FastAPI | Flask | Flask has no native async, no built-in SSE, no Pydantic integration. FastAPI is strictly superior for this use case. |
| Backend framework | FastAPI | Django | Massive overhead for a single-purpose API. No SSE story without channels. |
| SSE library | sse-starlette | raw StreamingResponse | sse-starlette handles keep-alive, W3C compliance, disconnect detection. Rolling your own wastes hackathon time. |
| Frontend framework | React + Vite | Next.js | SSR/SSG adds complexity with zero benefit for a single-page investigation dashboard. No SEO needed. |
| Frontend framework | React + Vite | Svelte | Smaller ecosystem, team familiarity matters in a 6-hour hackathon. |
| CSS | Tailwind CSS | shadcn/ui | shadcn adds a component abstraction layer. For a hackathon, raw Tailwind + custom components is faster to iterate. |
| Animation | motion | CSS animations | CSS keyframes cannot do AnimatePresence (mount/unmount), layout animations, or stagger orchestration needed for signal reveal. |
| Animation | motion | GSAP | GSAP's imperative API is slower to develop with in React. motion's declarative `<motion.div>` is faster to build. |
| Python HTTP | httpx | aiohttp | httpx has cleaner API, better typing, sync+async in one client. aiohttp is more complex for no benefit here. |
| AI client | openai SDK | LangChain | LangChain adds massive abstraction overhead for what is a single `parse()` call. Direct SDK is clearer and faster. |
| AI client | openai SDK | pydantic-ai | Interesting framework but adds learning curve. Direct openai SDK is simpler for a single-model, single-call pattern. |
| Package manager | uv | pip | pip is 10-100x slower. In a 6-hour hackathon, every second of environment setup matters. |
| State management | React useState/useReducer | Redux/Zustand | The app has one main state flow (investigation signals). useState with a reducer pattern is sufficient. No global state complexity. |
| WebSocket | SSE (EventSource) | WebSocket | SSE is simpler (unidirectional), auto-reconnects, works over HTTP/1.1, native browser API. Investigation is server-to-client only - no bidirectional need. |

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| LangChain / LangGraph | Massive abstraction for a single OpenAI call. Adds 50+ dependencies, debugging is opaque. Use the openai SDK directly. |
| Celery / task queues | The investigation pipeline is synchronous per-request (one user, one investigation). SSE streams the progress directly. No background worker needed. |
| Database (Postgres, SQLite) | No persistence required. Investigations are ephemeral. If you need to save results, write JSON to disk. Don't add DB setup time in a hackathon. |
| Redis | No caching layer needed. Each investigation is unique. No session state. |
| Docker | Adds deployment complexity with zero hackathon benefit. Run uvicorn directly. |
| Playwright / Puppeteer | TinyFish handles all browser automation. Adding your own browser layer defeats the purpose and doubles complexity. |
| BeautifulSoup / Scrapy | TinyFish replaces traditional scraping. Natural language goals > CSS selectors for anti-bot-protected sites. |
| Next.js / Remix | Server-side rendering adds complexity with no benefit for a single-page dashboard. |
| Zustand / Redux / Jotai | useState + useReducer handles the linear investigation flow. Don't add state management libraries for a single data stream. |

## Project Structure

```
fraudfish/
├── backend/
│   ├── main.py              # FastAPI app, SSE endpoint
│   ├── investigator.py       # Investigation pipeline orchestrator
│   ├── agents/
│   │   ├── listing.py        # TinyFish: extract listing details
│   │   ├── seller.py         # TinyFish: seller profile analysis
│   │   ├── market.py         # TinyFish: market rate scanning
│   │   └── official.py       # TinyFish: official site verification
│   ├── classifier.py         # OpenAI structured output classification
│   ├── rules.py              # Rules engine for obvious cases
│   ├── models.py             # Pydantic models (signals, verdicts, SSE events)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── hooks/
│   │   │   └── useInvestigation.ts  # SSE hook
│   │   ├── components/
│   │   │   ├── InvestigationView.tsx
│   │   │   ├── SignalCard.tsx
│   │   │   └── VerdictDisplay.tsx
│   │   └── types.ts          # Mirror backend Pydantic models
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Installation

```bash
# Backend (using uv)
cd backend
uv venv
source .venv/bin/activate
uv pip install fastapi==0.135.2 uvicorn==0.42.0 sse-starlette==3.3.3 openai==2.29.0 httpx==0.28.1 pydantic==2.12.5

# Or with requirements.txt
uv pip install -r requirements.txt

# Frontend
cd frontend
npm create vite@latest . -- --template react-ts
npm install motion tailwindcss @tailwindcss/vite
```

```bash
# Environment variables
export TINYFISH_API_KEY="provided-at-hackathon"
export OPENAI_API_KEY="provided-at-hackathon"
```

## Version Pinning Strategy

Pin major.minor, allow patch updates. For a hackathon, use `>=` to avoid version conflicts:

```txt
# requirements.txt
fastapi>=0.135.0
uvicorn>=0.42.0
sse-starlette>=3.3.0
openai>=2.29.0
httpx>=0.28.0
pydantic>=2.12.0
```

```json
// package.json (relevant deps)
{
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "motion": "^12.37.0"
  },
  "devDependencies": {
    "vite": "^8.0.0",
    "tailwindcss": "^4.2.0",
    "@tailwindcss/vite": "^4.2.0",
    "typescript": "^5.7.0"
  }
}
```

## Key Integration Points

### TinyFish SSE -> Backend SSE -> Frontend SSE

The critical architectural insight: TinyFish already streams via SSE. The backend receives TinyFish SSE events, enriches them into investigation signals, and re-streams them to the frontend via its own SSE endpoint. This creates a natural pipeline:

```
TinyFish SSE events -> FastAPI processes/enriches -> sse-starlette streams -> EventSource receives -> React renders with motion animations
```

Each TinyFish event becomes a signal card in the UI. No polling. No batching. Real-time evidence building.

### OpenAI Structured Output -> Pydantic -> Frontend Types

Define Pydantic models once in the backend. These same models:
1. Define the OpenAI `response_format` (structured output schema)
2. Validate the OpenAI response
3. Serialize to JSON for the SSE stream
4. Are mirrored as TypeScript types in the frontend

Single source of truth for data shapes across the entire stack.

## Sources

- [TinyFish Official Documentation](https://docs.tinyfish.ai)
- [TinyFish Web Agent](https://www.tinyfish.ai/)
- [TinyFish Python SDK](https://github.com/tinyfish-io/agent-sdk-python)
- [TinyFish Cookbook](https://github.com/tinyfish-io/tinyfish-cookbook)
- [FastAPI SSE Tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/)
- [FastAPI on PyPI](https://pypi.org/project/fastapi/) - v0.135.2
- [sse-starlette on PyPI](https://pypi.org/project/sse-starlette/) - v3.3.3
- [OpenAI Structured Outputs Guide](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI Python SDK on PyPI](https://pypi.org/project/openai/) - v2.29.0
- [uvicorn on PyPI](https://pypi.org/project/uvicorn/) - v0.42.0
- [Vite 8 Release](https://vite.dev/blog/announcing-vite8)
- [React 19.2](https://react.dev/blog/2025/10/01/react-19-2)
- [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4)
- [Motion (formerly Framer Motion)](https://motion.dev/docs/react)
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/)
