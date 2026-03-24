# Architecture Research

**Domain:** Autonomous web investigation agent (fraud detection)
**Researched:** 2026-03-24
**Confidence:** HIGH

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ URL Input    │  │ Investigation│  │ Verdict Display      │  │
│  │ Form         │  │ Feed (SSE)   │  │ + Evidence Cards     │  │
│  └──────┬───────┘  └──────▲───────┘  └──────────▲───────────┘  │
│         │                 │                      │              │
│         │          EventSource                   │              │
│         │          (streaming)            (final payload)       │
├─────────┼─────────────────┼──────────────────────┼──────────────┤
│         ▼                 │                      │              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FastAPI Backend (SSE Endpoint)              │    │
│  │  POST /investigate  →  async generator  →  SSE stream   │    │
│  └────────────────────────────┬────────────────────────────┘    │
│                               │                                 │
│  ┌────────────────────────────▼────────────────────────────┐    │
│  │              Investigation Orchestrator                   │    │
│  │  Runs pipeline steps sequentially, yields SSE events     │    │
│  └──┬──────┬──────┬──────┬──────┬──────┬───────────────────┘    │
│     │      │      │      │      │      │                        │
│     ▼      ▼      ▼      ▼      ▼      ▼                       │
│  ┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐                   │
│  │Step1││Step2││Step3││Step4││Step5││Step6│                   │
│  │List-││Sell-││Offic-││Cross││Mkt  ││Clas-│                   │
│  │ing  ││er   ││ial   ││Plat ││Rate ││sify │                   │
│  └──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘                   │
│     │      │      │      │      │      │                        │
├─────┼──────┼──────┼──────┼──────┼──────┼────────────────────────┤
│     ▼      ▼      ▼      ▼      ▼      ▼                       │
│  ┌──────────────────────────┐  ┌──────────────────────────┐     │
│  │   TinyFish Web Agent     │  │   OpenAI gpt-4o          │     │
│  │   (Steps 1-5: scraping)  │  │   (Step 6: classification)│     │
│  └──────────────────────────┘  └──────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **React Frontend** | URL input, SSE consumption, animated evidence reveal, verdict display | Vite + React, EventSource API, Tailwind CSS |
| **FastAPI SSE Endpoint** | Accept investigation request, return SSE stream | `POST /investigate` with `EventSourceResponse`, async generator |
| **Investigation Orchestrator** | Run pipeline steps in order, yield events after each step | Single async function that calls each step and yields `ServerSentEvent` |
| **TinyFish Steps (1-5)** | Web scraping via natural language goals | `TinyFish` Python SDK, `client.agent.stream()` per step |
| **Rules Engine** | Catch obvious fraud (extreme underpricing, impossible tickets) | Pure Python conditionals, no LLM call needed |
| **OpenAI Classifier (Step 6)** | Synthesize all signals into verdict with reasoning | `openai.chat.completions.create()` with structured output |
| **Signal Aggregator** | Collect outputs from steps 1-5 into a unified evidence dict | Python dict accumulation within orchestrator |

## Recommended Project Structure

```
fraudfish/
├── backend/
│   ├── main.py                # FastAPI app, CORS, SSE endpoint
│   ├── orchestrator.py        # Investigation pipeline controller
│   ├── steps/
│   │   ├── __init__.py
│   │   ├── extract_listing.py # Step 1: Extract listing details
│   │   ├── check_seller.py    # Step 2: Seller profile investigation
│   │   ├── check_official.py  # Step 3: Official ticket site check
│   │   ├── cross_platform.py  # Step 4: Cross-platform search
│   │   └── market_rate.py     # Step 5: Market rate comparison
│   ├── classifier.py          # OpenAI classification + rules engine
│   ├── models.py              # Pydantic models for events + verdict
│   ├── tinyfish_client.py     # TinyFish SDK wrapper with retry
│   └── config.py              # API keys, settings
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main app, routing
│   │   ├── hooks/
│   │   │   └── useInvestigation.ts  # SSE hook for investigation stream
│   │   ├── components/
│   │   │   ├── URLInput.tsx         # Paste URL form
│   │   │   ├── InvestigationFeed.tsx # Animated signal cards
│   │   │   ├── SignalCard.tsx        # Individual evidence card
│   │   │   └── VerdictDisplay.tsx    # Final verdict + reasoning
│   │   └── types.ts                 # TypeScript types matching backend models
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

### Structure Rationale

- **backend/steps/**: Each investigation step is its own module. Isolation means you can develop, test, and mock each step independently. When TinyFish APIs are unavailable pre-hackathon, you mock at this boundary.
- **backend/orchestrator.py**: Single file controls the entire pipeline flow. This is the core of the system. Keeping it as one function with clear step calls makes the 6-hour timeline manageable.
- **backend/classifier.py**: Separates OpenAI classification logic from web scraping logic. Rules engine lives here too since both produce the same verdict type.
- **frontend/hooks/useInvestigation.ts**: One custom hook encapsulates all SSE state. Components stay dumb.

## Architectural Patterns

### Pattern 1: Pipeline-as-Generator (Core Pattern)

**What:** The investigation orchestrator is a single async generator function. Each `yield` emits an SSE event to the frontend. Steps execute sequentially within the generator.

**When to use:** When you have a linear pipeline of steps that must stream intermediate results to a client. This is the entire backend architecture.

**Trade-offs:** Simple to build and debug. Sequential execution means total time is sum of all steps (not parallelized). For a 6-hour hackathon, simplicity beats speed.

**Example:**
```python
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

class InvestigationEvent(BaseModel):
    step: str
    status: str  # "running" | "complete" | "error"
    data: dict | None = None

app = FastAPI()

@app.post("/investigate", response_class=EventSourceResponse)
async def investigate(request: InvestigateRequest):
    async def pipeline():
        evidence = {}

        # Step 1: Extract listing
        yield ServerSentEvent(
            data=InvestigationEvent(step="extract_listing", status="running"),
            event="step"
        )
        listing = await extract_listing(request.url)
        evidence["listing"] = listing
        yield ServerSentEvent(
            data=InvestigationEvent(step="extract_listing", status="complete", data=listing),
            event="step"
        )

        # Step 2: Check seller... (same pattern)
        # ...

        # Step 6: Classify
        verdict = await classify(evidence)
        yield ServerSentEvent(
            data=InvestigationEvent(step="verdict", status="complete", data=verdict),
            event="verdict"
        )

    return EventSourceResponse(pipeline())
```

### Pattern 2: TinyFish Task Wrapper

**What:** Each investigation step wraps a single TinyFish `client.agent.stream()` call with a natural-language goal. The wrapper handles SSE consumption from TinyFish, extracts the final result, and returns structured data.

**When to use:** Every step that needs to scrape a webpage.

**Trade-offs:** TinyFish SSE events are consumed server-side (not forwarded to frontend). The backend processes TinyFish output and emits its own simplified SSE events to the frontend. This decouples the frontend from TinyFish's event format.

**Example:**
```python
from tinyfish import TinyFish

client = TinyFish()  # Uses TINYFISH_API_KEY env var

async def extract_listing(url: str) -> dict:
    result = None
    with client.agent.stream(
        url=url,
        goal=(
            "Extract: listing title, price, seller username, description, "
            "ticket transfer method (e-ticket/physical/unspecified), "
            "event name, event date. Return as JSON."
        ),
    ) as stream:
        for event in stream:
            if event.get("type") == "COMPLETE":
                result = event.get("result")
    return result or {}
```

### Pattern 3: Two-Tier Classification

**What:** A rules engine handles obvious cases (price < 20% of face value = LIKELY_SCAM; price > 500% = SCALPING_VIOLATION). Only ambiguous cases go to OpenAI for LLM reasoning.

**When to use:** Always. The rules engine runs first. If it produces a high-confidence verdict, skip the LLM call entirely (saves time and credits).

**Trade-offs:** Rules are brittle but fast and free. LLM is flexible but slow and costs credits. The combination gives speed for obvious cases and nuance for hard cases.

**Example:**
```python
def rules_check(evidence: dict) -> dict | None:
    """Return verdict if obvious, None if needs LLM."""
    listing_price = evidence.get("listing", {}).get("price", 0)
    face_value = evidence.get("official", {}).get("face_value", 0)

    if face_value > 0 and listing_price < face_value * 0.2:
        return {
            "category": "LIKELY_SCAM",
            "confidence": 0.95,
            "reasoning": f"Listed at {listing_price} vs face value {face_value} - extreme underpricing is a classic scam indicator"
        }
    # ... more rules
    return None  # Needs LLM

async def classify(evidence: dict) -> dict:
    quick = rules_check(evidence)
    if quick:
        return quick
    return await llm_classify(evidence)
```

### Pattern 4: SSE Event Protocol

**What:** Define a small, fixed set of SSE event types that the frontend listens for. Keep the protocol simple.

**When to use:** This is the contract between backend and frontend. Define it early, build both sides against it.

**Event types:**
```
event: step        → Investigation step status update (running/complete/error)
event: verdict     → Final classification result
event: error       → Unrecoverable error
event: done        → Stream complete (signals frontend to close EventSource)
```

**Example event payloads:**
```
event: step
data: {"step": "extract_listing", "status": "running", "label": "Extracting listing details..."}

event: step
data: {"step": "extract_listing", "status": "complete", "data": {"title": "F1 Pit Grandstand", "price": 3500, "seller": "ticketking88"}}

event: verdict
data: {"category": "SCALPING_VIOLATION", "confidence": 0.87, "reasoning": "Listed at 2.3x face value..."}

event: done
data: {}
```

## Data Flow

### Primary Investigation Flow

```
User pastes URL
    ↓
React: POST /investigate {url: "https://carousell.sg/p/..."}
    ↓
FastAPI: starts async generator pipeline
    ↓
    ├── Step 1: TinyFish → listing URL → extract details
    │   yield SSE {step: "extract_listing", status: "complete", data: {...}}
    │   React: renders SignalCard with listing details
    ↓
    ├── Step 2: TinyFish → seller profile URL → extract trust signals
    │   yield SSE {step: "check_seller", status: "complete", data: {...}}
    │   React: renders SignalCard with seller info
    ↓
    ├── Step 3: TinyFish → SISTIC/Ticketmaster → extract face value
    │   yield SSE {step: "check_official", status: "complete", data: {...}}
    │   React: renders SignalCard with price comparison
    ↓
    ├── Step 4: TinyFish → other marketplaces → find duplicates
    │   yield SSE {step: "cross_platform", status: "complete", data: {...}}
    │   React: renders SignalCard with cross-platform findings
    ↓
    ├── Step 5: TinyFish → marketplace search → calculate market rate
    │   yield SSE {step: "market_rate", status: "complete", data: {...}}
    │   React: renders SignalCard with market rate comparison
    ↓
    ├── Step 6: Rules engine check → if obvious, skip LLM
    │   OR: OpenAI gpt-4o → synthesize all evidence → structured verdict
    │   yield SSE {event: "verdict", data: {category, confidence, reasoning}}
    │   React: renders VerdictDisplay with animated reveal
    ↓
    └── yield SSE {event: "done"}
        React: closes EventSource, enables "Investigate Another" button
```

### Frontend State Machine

```
IDLE → CONNECTING → INVESTIGATING → VERDICT → IDLE
                        │
                        ├── on "step" event: append to signals[]
                        ├── on "verdict" event: set verdict
                        ├── on "error" event: show error, go IDLE
                        └── on "done" event: go IDLE (with verdict shown)
```

### React SSE Consumption

```typescript
// hooks/useInvestigation.ts
function useInvestigation() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [verdict, setVerdict] = useState<Verdict | null>(null);
  const [status, setStatus] = useState<"idle" | "investigating" | "error">("idle");

  const investigate = useCallback((url: string) => {
    setSignals([]);
    setVerdict(null);
    setStatus("investigating");

    // POST-based SSE requires fetch, not EventSource
    fetch("/api/investigate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    }).then(async (response) => {
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      // Parse SSE stream from ReadableStream...
    });
  }, []);

  return { signals, verdict, status, investigate };
}
```

**Important note:** The native `EventSource` API only supports GET requests. Since the investigation endpoint is POST (to send the URL in the body), the frontend must use `fetch()` with a `ReadableStream` reader to consume the SSE stream. This is a common pattern for POST-based SSE.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Hackathon demo (1-5 concurrent) | Single FastAPI process, sequential steps, no database. This is the target. |
| 100 concurrent users | Add asyncio.gather() for independent TinyFish steps (2-4 could run in parallel). Add Redis for caching repeat investigations. |
| 1000+ concurrent users | Worker queue (Celery/ARQ) to offload TinyFish calls. Multiple FastAPI workers behind reverse proxy. Database for investigation history. |

### Scaling Priorities

1. **First bottleneck:** TinyFish API rate limits and response time. Each step takes 5-15 seconds. Total investigation: 30-60 seconds. No fix needed for hackathon demo.
2. **Second bottleneck:** Sequential step execution. Steps 3, 4, 5 are independent and could run in parallel with asyncio.gather(). Only optimize if demo feels too slow.

## Anti-Patterns

### Anti-Pattern 1: Forwarding Raw TinyFish SSE to Frontend

**What people do:** Pipe TinyFish's SSE events directly through to the React frontend, exposing internal browsing states.
**Why it is wrong:** TinyFish emits many low-level events (page navigating, element found, scrolling). The frontend does not need or want these. It creates a brittle coupling between TinyFish's event format and your UI.
**Do this instead:** Consume TinyFish events server-side. Emit your own simplified events (step running/complete) to the frontend.

### Anti-Pattern 2: Building a Generic Agent Framework

**What people do:** Create abstract Agent, Tool, Memory classes trying to build a reusable agent system.
**Why it is wrong:** You have 6 hours. The investigation pipeline has exactly 5-6 known steps. There is nothing to generalize.
**Do this instead:** Write the orchestrator as a single async function with explicit step calls. Hardcode the pipeline. Refactor never (it is a hackathon).

### Anti-Pattern 3: Database-First Architecture

**What people do:** Set up PostgreSQL, create schema, build CRUD endpoints for investigations.
**Why it is wrong:** There is no persistence requirement. No user accounts. No history. Adding a database costs 1-2 hours of the 6-hour budget for zero demo value.
**Do this instead:** Keep all state in-memory within the SSE generator. The investigation starts, streams, and ends. Nothing persists.

### Anti-Pattern 4: Microservice Decomposition

**What people do:** Separate the scraping service, classification service, and API gateway into different processes.
**Why it is wrong:** One person, 6 hours, one demo machine. Multiple processes means multiple things that can break, multiple deployments, multiple logs to check.
**Do this instead:** Single FastAPI process. Everything in one Python process. Monolith is the correct architecture for this scope.

### Anti-Pattern 5: Using EventSource API for POST Requests

**What people do:** Try to use the browser's native `EventSource` for POST-based SSE endpoints.
**Why it is wrong:** `EventSource` only supports GET requests. It will silently fail or require a library polyfill.
**Do this instead:** Use `fetch()` with `ReadableStream` reader to consume POST-based SSE. Parse the `text/event-stream` format manually (it is simple: split on `\n\n`, parse `event:` and `data:` lines).

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| TinyFish Web Agent | Python SDK `client.agent.stream()` per step. Natural language goals, returns structured JSON. | API key via env var. SSE streaming from TinyFish consumed server-side. Browser profile "stealth" for anti-bot sites (Carousell). |
| OpenAI gpt-4o | `openai` Python SDK. `chat.completions.create()` with structured output (response_format). | Used only in classification step. System prompt defines verdict categories and evidence format. |
| Target sites (Carousell, Viagogo, SISTIC) | Accessed via TinyFish, not directly. TinyFish handles anti-bot, rendering, navigation. | No direct HTTP requests to target sites from backend. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| React <-> FastAPI | SSE over HTTP (POST). JSON payloads. CORS required. | Define event types as shared contract. Frontend uses fetch + ReadableStream. |
| Orchestrator <-> Steps | Direct async function calls. Each step returns a dict. | No message queue, no events. Simple function calls within one process. |
| Orchestrator <-> Classifier | Direct async function call. Passes accumulated evidence dict. | Rules engine checked first, OpenAI only if rules are inconclusive. |
| Steps <-> TinyFish SDK | SDK handles HTTP/SSE to TinyFish API. Steps provide URL + goal string. | Wrap in try/except. Return partial data on failure (investigation continues with available evidence). |

## Suggested Build Order

Based on dependency analysis, build in this order:

| Order | Component | Depends On | Time Estimate | Why This Order |
|-------|-----------|------------|---------------|----------------|
| 1 | **Pydantic models** (models.py) | Nothing | 15 min | Defines the contract everything else builds against |
| 2 | **FastAPI SSE endpoint** (main.py) | Models | 20 min | Prove SSE streaming works end-to-end with mock data |
| 3 | **React SSE hook + skeleton UI** | SSE endpoint | 45 min | Connect frontend to backend stream. Verify events render. |
| 4 | **TinyFish wrapper** (tinyfish_client.py) | Models | 15 min | Thin wrapper with error handling around SDK |
| 5 | **Step 1: Extract listing** | TinyFish wrapper | 20 min | First real step. Proves TinyFish integration works. |
| 6 | **Orchestrator with Step 1** | Step 1, SSE endpoint | 15 min | Wire first step into the SSE pipeline |
| 7 | **Steps 2-5** | TinyFish wrapper | 60 min | Each step is the same pattern: URL + goal + parse result |
| 8 | **Rules engine + OpenAI classifier** | Models | 30 min | Classification logic, independent of scraping steps |
| 9 | **Full orchestrator** (all steps + classifier) | Steps 1-5, classifier | 20 min | Wire everything together |
| 10 | **UI polish** (signal cards, verdict display, animations) | Working SSE stream | 60 min | Make it demo-worthy |
| 11 | **Event scan mode** (if time permits) | Full pipeline working | 45 min | Bonus feature: scan multiple listings for one event |

**Critical path:** Models -> SSE endpoint -> React hook -> TinyFish wrapper -> Steps -> Orchestrator -> Classifier -> UI polish

**Mock-first strategy:** Build steps 1-7 pre-hackathon with mock TinyFish responses. On hackathon day, swap mocks for real SDK calls (step 5 becomes real, everything else already works).

## Sources

- [FastAPI SSE Tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/) - Official docs, EventSourceResponse + ServerSentEvent API (added in FastAPI 0.135.0)
- [TinyFish Web Agent Docs](https://docs.tinyfish.ai) - API endpoint, authentication, SSE response format
- [TinyFish Python SDK](https://github.com/tinyfish-io/agent-sdk-python) - client.agent.stream() API
- [TinyFish Cookbook](https://github.com/tinyfish-io/tinyfish-cookbook) - 26 recipes showing multi-site parallel patterns
- [Google Cloud Agentic AI Design Patterns](https://docs.google.com/architecture/choose-design-pattern-agentic-ai-system) - Sequential orchestration pattern reference
- [React SSE Implementation](https://oneuptime.com/blog/post/2026-01-15-server-sent-events-sse-react/view) - POST-based SSE with fetch + ReadableStream

---
*Architecture research for: FraudFish autonomous fraud investigation agent*
*Researched: 2026-03-24*
