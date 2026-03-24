# Project Research Summary

**Project:** FraudFish - Autonomous Fraud Intelligence Agent
**Domain:** Real-time web investigation agent (fraud detection for ticket marketplace scams)
**Researched:** 2026-03-24
**Confidence:** HIGH

## Executive Summary

FraudFish is an autonomous fraud investigation agent built for a 6-hour solo TinyFish hackathon. The product takes a marketplace listing URL (Carousell, Viagogo), dispatches TinyFish web agents to gather evidence across multiple sites (listing details, seller profile, official ticket prices, cross-platform duplicates), classifies the listing using a rules engine plus OpenAI gpt-4o structured output, and streams the entire investigation to the user in real-time via SSE. The core demo value is watching the agent work -- evidence cards appearing one-by-one as the investigation progresses, culminating in an authoritative verdict with reasoning.

The recommended approach is a Python/FastAPI backend with a pipeline-as-generator architecture, where each investigation step yields SSE events to a React frontend. TinyFish handles all browser automation (no Playwright/Selenium), OpenAI handles ambiguous classification (with a rules engine catching obvious cases first), and the frontend uses motion (framer-motion) for signal-by-signal animated reveal. The stack is deliberately minimal: no database, no auth, no task queue, no state management library. Every technology choice optimizes for hackathon velocity and demo impact.

The primary risks are: (1) TinyFish calls taking too long when run sequentially (must parallelize independent steps), (2) Carousell's Cloudflare protection blocking scraping during the live demo (must have cached fallback data), (3) OpenAI structured output schema rejecting common Pydantic patterns at runtime (must pre-validate schemas), and (4) the solo builder spending too much time on integration plumbing instead of demo-worthy features (must pre-build the application skeleton before hackathon day). All four risks have concrete mitigation strategies detailed in the research.

## Key Findings

### Recommended Stack

The stack splits into a Python backend (FastAPI + TinyFish SDK + OpenAI SDK) and a TypeScript frontend (React + Vite + Tailwind + motion). All choices are HIGH confidence with well-documented integration paths.

**Core technologies:**
- **FastAPI 0.135.2**: API framework -- native SSE support via EventSourceResponse, async-first, Pydantic integration for structured data flow
- **TinyFish Python SDK**: Web agent -- `client.agent.stream()` returns SSE events natively, natural language goals replace brittle CSS selectors
- **OpenAI SDK 2.29.0 + gpt-4o**: Classification -- `chat.completions.parse()` with Pydantic models for guaranteed structured verdict output
- **sse-starlette 3.3.3**: SSE implementation -- W3C-compliant, handles keep-alive pings and disconnect detection automatically
- **React 19.2 + Vite 8 + TypeScript**: Frontend -- native EventSource/fetch for SSE consumption, motion for animated signal reveal
- **Tailwind CSS 4.2**: Styling -- zero-config in v4, fastest path to polished hackathon UI
- **uv**: Python package manager -- 10-100x faster than pip, critical for hackathon setup speed

**Explicitly excluded:** LangChain (massive abstraction for a single API call), databases (no persistence needed), Docker (deployment overhead), Playwright/Puppeteer (TinyFish replaces these), Next.js (SSR adds complexity with zero benefit), Redux/Zustand (useState suffices for linear data flow).

### Expected Features

**Must have (table stakes -- demo fails without these):**
- URL input triggering autonomous investigation
- Listing detail extraction via TinyFish (price, seller, event, description)
- Seller profile investigation (account age, ratings, listing history)
- Price comparison against official ticket sources (SISTIC/Ticketmaster)
- Real-time SSE streaming of investigation steps to UI
- Evidence cards rendering as steps complete
- Final verdict with classification, confidence score, and natural language reasoning

**Should have (differentiators -- what wins the hackathon):**
- Cross-platform correlation (search same event on second marketplace)
- Signal-by-signal animated reveal with risk color coding (green/yellow/red)
- Rules engine for obvious cases (skip LLM for extreme over/underpricing)
- Validation layer catching LLM classification mistakes

**Defer (build only if core is rock-solid):**
- Event scan mode (investigate multiple listings for one event)
- Threat intelligence dashboard (aggregate scan results)
- Telegram group scraping, PDF reports, database persistence, mobile responsive

### Architecture Approach

The system follows a pipeline-as-generator pattern: a single async generator function in the orchestrator runs investigation steps sequentially, yielding SSE events after each step. TinyFish SSE events are consumed server-side and re-emitted as simplified investigation signals to the frontend. The frontend is a state machine (IDLE -> CONNECTING -> INVESTIGATING -> VERDICT -> IDLE) driven entirely by SSE events. No WebSockets, no polling, no shared state.

**Major components:**
1. **React Frontend** -- URL input, SSE consumption via fetch/ReadableStream, animated evidence card reveal, verdict display
2. **FastAPI SSE Endpoint** -- accepts POST /investigate, returns EventSourceResponse backed by async generator
3. **Investigation Orchestrator** -- runs pipeline steps in order, accumulates evidence dict, yields SSE events
4. **TinyFish Step Modules** -- each step wraps a single TinyFish call with a specific natural-language goal, returns structured data
5. **Two-Tier Classifier** -- rules engine for obvious cases, OpenAI gpt-4o structured output for ambiguous cases

**Key architectural decisions:**
- POST-based SSE (not GET) requires fetch + ReadableStream on the frontend, not native EventSource
- TinyFish events are NOT forwarded raw to the frontend -- backend processes and simplifies them
- Single FastAPI process (monolith) -- no microservices for a solo hackathon
- Independent steps (seller check, official check, cross-platform) can be parallelized with asyncio.gather() after initial listing extraction

### Critical Pitfalls

1. **Sequential TinyFish calls blow the time budget** -- Each call takes 15-45 seconds. Running 4-6 calls sequentially means 90-270 second investigations. Must parallelize independent steps with asyncio.gather() from the start.
2. **Carousell Cloudflare blocks live demo** -- Cloudflare Enterprise detection is probabilistic and may fail during demo from hackathon venue IP. Must pre-scrape fallback fixtures and have Viagogo as alternate demo target.
3. **OpenAI structured output schema rejected at runtime** -- All fields must be required, no Field() validators, no Dict types, no recursive schemas. Must pre-validate with openai.pydantic_function_tool() before hackathon day.
4. **SSE stream appears frozen** -- Buffering, missing CORS, no heartbeat cause events to batch or drop. Must set proper headers, use sse-starlette, send heartbeats every 5 seconds, and test SSE first (not last).
5. **Solo builder wastes time on plumbing** -- Integration debugging (auth, CORS, SSE, schema) can consume 3+ of 6 hours. Must pre-build entire application skeleton with mocks before hackathon day.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 0: Pre-Work Skeleton
**Rationale:** Pitfall 5 (time waste) is the meta-risk that kills everything else. The entire application skeleton, mock pipeline, and validated schemas must exist before hackathon day. This is the single most impactful phase.
**Delivers:** Complete working application with mock data -- FastAPI app with SSE endpoint, React app with SSE consumer and animated signal cards, Pydantic models pre-validated against OpenAI schema constraints, mock TinyFish responses exercising the full pipeline.
**Addresses:** URL input, SSE streaming, evidence cards, verdict display (all with mock data)
**Avoids:** Pitfall 3 (OpenAI schema errors), Pitfall 4 (SSE buffering), Pitfall 5 (plumbing time waste)

### Phase 1: Core Investigation Pipeline
**Rationale:** This is the hero demo flow. Without live TinyFish extraction working, there is no product. Must be the first thing built on hackathon day.
**Delivers:** Live TinyFish integration for listing extraction, seller profile, and official price check. Rules engine for obvious cases. OpenAI classification for ambiguous cases. End-to-end investigation from URL to verdict with real data.
**Addresses:** Listing detail extraction, seller profile investigation, price comparison, rules engine, final verdict
**Avoids:** Pitfall 1 (sequential calls -- design parallel architecture from start), Pitfall 6 (goal prompt failures -- iterate prompts against real listings)

### Phase 2: Differentiators and Intelligence
**Rationale:** Core flow must work before adding cross-platform correlation and polish. These features separate "working demo" from "winning demo."
**Delivers:** Cross-platform search (find same event on other marketplace), validation layer (catch LLM mistakes), confidence calibration display.
**Addresses:** Cross-platform correlation, validation layer, confidence calibration
**Avoids:** Pitfall 7 (unhandled edge cases -- add error handling for each signal)

### Phase 3: Demo Hardening and Polish
**Rationale:** A polished, reliable demo beats a feature-rich, buggy demo. This phase makes the difference between "it works" and "it impresses."
**Delivers:** Signal-by-signal animated reveal with risk color coding, cached fallback fixtures for demo resilience, pre-tested demo URLs, edge case handling (deleted listings, private profiles), demo script rehearsal.
**Addresses:** Signal animation, demo resilience, professional polish
**Avoids:** Pitfall 2 (Cloudflare blocking during demo), Pitfall 7 (demo crashes on edge cases)

### Phase 4: Stretch Goals (Time Permitting)
**Rationale:** Only attempt if Phases 0-3 are solid. Event scan mode multiplies the core flow -- if the core is broken, this amplifies the brokenness.
**Delivers:** Event scan mode (search by event name, investigate multiple listings), threat intelligence summary.
**Addresses:** Event scan mode, threat intelligence dashboard

### Phase Ordering Rationale

- **Phase 0 before hackathon day** because integration debugging is the number one time killer for solo hackathon builders. Every minute spent on CORS, SSE buffering, or schema errors on demo day is a minute not spent on investigation logic.
- **Phase 1 first on hackathon day** because TinyFish integration is the highest-risk, highest-value component. If it does not work, the fallback plan must activate immediately.
- **Phase 2 before Phase 3** because cross-platform correlation is the strongest differentiator for judges evaluating "agentic web intelligence." Polish without this feature is less compelling than this feature without polish.
- **Phase 3 before Phase 4** because demo reliability trumps feature count. Judges remember crashes. A smooth single-investigation demo beats a buggy multi-investigation demo.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** TinyFish goal prompts need iteration against real listings for each target site. The exact prompt wording significantly affects extraction quality. Plan for prompt engineering time.
- **Phase 2:** Cross-platform correlation depends on TinyFish successfully searching a second marketplace -- the search interaction is more complex than single-page extraction and has higher failure risk.

Phases with standard patterns (skip research-phase):
- **Phase 0:** All technologies are well-documented. FastAPI SSE, React EventSource, Pydantic models -- established patterns with official tutorials.
- **Phase 3:** Animation with motion and demo hardening are straightforward execution. Prior project (ducket-ai) validated the signal-by-signal reveal pattern.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All technologies have official docs, PyPI/npm packages verified with current versions. FastAPI SSE, OpenAI structured output, TinyFish SDK all have working examples. |
| Features | HIGH | Feature prioritization grounded in hackathon judging criteria, validated by prior project (ducket-ai). Demo script alignment is clear. |
| Architecture | HIGH | Pipeline-as-generator is a well-documented pattern. Build order has clear dependency chain. Anti-patterns are specific and actionable. |
| Pitfalls | MEDIUM-HIGH | TinyFish-specific pitfalls rely on sparse error handling docs. Cloudflare blocking risk is real but mitigation (fallback data) is proven. OpenAI schema constraints well-documented. |

**Overall confidence:** HIGH

### Gaps to Address

- **TinyFish rate limits and concurrent session limits:** Documentation is sparse on how many parallel agent sessions one API key supports. Must test during Phase 1 and have sequential fallback if parallel calls are rate-limited.
- **TinyFish stealth mode effectiveness on Carousell:** No guarantee stealth + proxy will consistently bypass Cloudflare Enterprise. Must test from hackathon venue network and have cached fallback ready.
- **Exact TinyFish SDK async API:** Research references `client.agent.stream()` but the async variant for use with asyncio.gather() needs verification. May need httpx fallback for direct REST calls.
- **Hackathon-day API credit availability:** OpenAI and TinyFish credits are "provided at hackathon." Must have a plan for the window between setup and credit distribution (use mocks).

## Sources

### Primary (HIGH confidence)
- [TinyFish Official Documentation](https://docs.tinyfish.ai) -- SDK API, SSE format, stealth mode, goal-based extraction
- [TinyFish Python SDK](https://github.com/tinyfish-io/agent-sdk-python) -- client.agent.stream() API
- [TinyFish Cookbook](https://github.com/tinyfish-io/tinyfish-cookbook) -- 26 recipes, multi-site patterns
- [FastAPI SSE Tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/) -- EventSourceResponse + ServerSentEvent (v0.135.0+)
- [OpenAI Structured Outputs Guide](https://developers.openai.com/api/docs/guides/structured-outputs) -- schema constraints, Pydantic integration
- [OpenAI Python SDK on PyPI](https://pypi.org/project/openai/) -- v2.29.0
- [Pydantic v2 Docs](https://docs.pydantic.dev/latest/) -- model validation, JSON schema generation

### Secondary (MEDIUM confidence)
- [Cloudflare Carousell Case Study](https://www.cloudflare.com/case-studies/carousell/) -- confirms Cloudflare Enterprise usage
- [OpenAI Community Forums](https://community.openai.com) -- structured output edge cases and workarounds
- [Motion (formerly Framer Motion) Docs](https://motion.dev/docs/react) -- AnimatePresence, layout animations
- [Vite 8 Release Blog](https://vite.dev/blog/announcing-vite8) -- Rolldown engine, performance claims
- [React SSE Implementation Guide](https://oneuptime.com/blog/post/2026-01-15-server-sent-events-sse-react/view) -- POST-based SSE with fetch

### Tertiary (LOW confidence)
- [TinyFish LLMs.txt](https://docs.tinyfish.ai/llms.txt) -- sync/async/SSE/batch endpoints, cancellation limits (machine-generated docs)
- Hackathon time management and pitfall articles -- general patterns applied to this specific context

---
*Research completed: 2026-03-24*
*Ready for roadmap: yes*
