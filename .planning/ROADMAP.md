# Roadmap: FraudFish

## Overview

FraudFish is built across two time windows: pre-work (now through March 27) and hackathon day (March 28, 6 hours). The pre-work phase builds the complete application skeleton with mock data -- FastAPI SSE backend, React animated UI, Pydantic models, and the full investigation flow running on cached responses. This eliminates all integration plumbing on hackathon day. On March 28, the five remaining phases swap mocks for live TinyFish and OpenAI calls, add cross-platform intelligence, and finish with event scan mode. Every phase delivers a working, demoable state of the application.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Application Skeleton with Mocks** - Complete working app (frontend + backend + SSE streaming + animated UI) using mock data, buildable before hackathon day
- [x] **Phase 2: Core Investigation Pipeline** - Live TinyFish integration for listing extraction, seller profile, and official price verification (completed 2026-03-25)
- [ ] **Phase 3: Classification and Verdict Engine** - Rules engine for obvious cases, OpenAI gpt-4o for ambiguous cases, validation layer to catch mistakes
- [x] **Phase 4: Cross-Platform Intelligence** - Market rate calculation from multiple listings and cross-platform duplicate detection (completed 2026-03-25)
- [ ] **Phase 5: Event Scan Mode** - Batch investigation by event name with threat intelligence summary

## Phase Details

### Phase 1: Application Skeleton with Mocks
**Goal**: A user can paste a URL, watch an animated investigation unfold with mock data, and see a verdict -- the complete UI and streaming architecture works end-to-end without any live API calls
**Depends on**: Nothing (first phase)
**Requirements**: PIPE-01, PIPE-08, RTUI-01, RTUI-02, RTUI-03, RTUI-04, RTUI-05, RTUI-06, RTUI-07, RTUI-08, RTUI-09, CLAS-03, CLAS-05
**Success Criteria** (what must be TRUE):
  1. User can paste a URL into the input field and click "Investigate" to start a mock investigation
  2. Six investigation step cards appear sequentially with PENDING -> ACTIVE -> COMPLETE state transitions and staggered entrance animations
  3. Each completed step card displays realistic mock evidence data (extracted listing details, seller info, price comparisons)
  4. Final verdict panel renders with color-coded classification category, confidence score percentage, and expandable natural language reasoning
  5. Five risk indicator meters display with severity bars, and the evidence sidebar shows seller summary and price comparison chart -- all following the DESIGN.md design system
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md -- FastAPI backend with Pydantic models, mock F1 GP data, and SSE streaming endpoint
- [x] 01-02-PLAN.md -- React frontend with Tailwind v4 design system, SSE client, investigation hook, and animated timeline
- [ ] 01-03-PLAN.md -- VerdictPanel, EvidenceSidebar, end-to-end wiring, and visual verification

### Phase 2: Core Investigation Pipeline
**Goal**: The agent autonomously extracts real listing data, investigates the seller profile, and verifies event details against official ticket sites -- all via live TinyFish calls running in parallel where independent
**Depends on**: Phase 1
**Requirements**: PIPE-02, PIPE-03, PIPE-04, PIPE-07
**Success Criteria** (what must be TRUE):
  1. User pastes a real Carousell or Viagogo listing URL and the agent extracts actual price, seller name, description, transfer method, and posting date from the live page
  2. Agent navigates to the seller's profile and returns real account age, total listings, listing categories, and review sentiment
  3. Agent checks at least one official ticket site (SISTIC, Ticketmaster SG, or F1 official) and returns real face value and sold-out status for the event
  4. Independent investigation steps (seller profile, official price check) run in parallel via asyncio.gather and the full investigation completes within 60 seconds
**Plans**: 4 plans

Plans:
- [ ] 02-01-PLAN.md -- TinyFish base agent wrapper, platform detection, Carousell and Telegram listing extractors
- [ ] 02-02-PLAN.md -- Seller profile investigation (Carousell full review parsing, Telegram repeat-seller detection)
- [ ] 02-03-PLAN.md -- Official price verification (Ticketmaster SG, F1 official, Google fallback)
- [ ] 02-04-PLAN.md -- Parallel investigation orchestrator, SSE wiring, and LIVE badge

### Phase 3: Classification and Verdict Engine
**Goal**: The system produces accurate, evidence-backed verdicts -- obvious fraud is caught instantly by rules, ambiguous cases get reasoned LLM classification, and a validation layer prevents embarrassing mistakes
**Depends on**: Phase 2
**Requirements**: CLAS-01, CLAS-02, CLAS-04
**Success Criteria** (what must be TRUE):
  1. A listing priced at less than 40% of face value is classified as LIKELY_SCAM by the rules engine without making an LLM call
  2. A listing with ambiguous signals (moderate markup, new seller, real event) receives a reasoned classification from OpenAI gpt-4o with structured JSON output including category, confidence, and natural language explanation
  3. The validation layer overrides an incorrect LLM classification (e.g., prevents LEGITIMATE verdict on a listing with extreme underpricing) and the correction is visible in the verdict reasoning
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md -- Rules engine with centralized config, deterministic classification, and validation layer with contradiction checks
- [ ] 03-02-PLAN.md -- OpenAI gpt-4o structured output classification, two-tier orchestrator, and LLM error fallback

### Phase 4: Cross-Platform Intelligence
**Goal**: The agent goes beyond single-listing analysis by scanning the broader market for the same event and detecting sellers cross-posting across platforms -- the "investigation" that makes FraudFish an intelligence agent, not just a classifier
**Depends on**: Phase 2
**Requirements**: PIPE-05, PIPE-06
**Success Criteria** (what must be TRUE):
  1. Agent scans 10+ other listings for the same event across platforms and displays the calculated market rate alongside the investigated listing's price, with statistical outliers highlighted
  2. Agent searches at least one other marketplace for the same seller name or listing text and reports whether cross-platform duplicates were found
**Plans**: 2 plans

Plans:
- [ ] 04-01-PLAN.md -- Stats module, market scan agent, cross-platform duplicate agent, and unit tests
- [ ] 04-02-PLAN.md -- Pipeline integration, StepCard formatting, EvidenceSidebar outlier label and cross-platform matches

### Phase 5: Event Scan Mode
**Goal**: Users can investigate an entire event's fraud landscape in one action -- enter an event name, the agent discovers and investigates multiple listings, and produces a threat intelligence summary showing the scale of suspicious activity
**Depends on**: Phase 3, Phase 4
**Requirements**: SCAN-01, SCAN-02, SCAN-03, SCAN-04
**Success Criteria** (what must be TRUE):
  1. User can enter an event name (e.g., "F1 Singapore Grand Prix 2026") and the agent searches Carousell and Viagogo for matching listings
  2. Agent runs the full investigation pipeline on each discovered listing and streams progress for all investigations
  3. Threat intelligence summary displays total listings found, flagged suspicious count, confirmed likely scam count, and estimated fraud exposure in SGD
**Plans**: 3 plans

Plans:
- [ ] 05-01-PLAN.md -- Backend scan pipeline orchestrator, /api/scan SSE endpoint, Pydantic models, and tests
- [ ] 05-02-PLAN.md -- Frontend scan types, SSE client, useEventScan hook, and InputSection tab toggle
- [ ] 05-03-PLAN.md -- ThreatSummary banner, ScanListingRow with expand/collapse, ScanResults container, App.tsx wiring

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5
Note: Phase 3 and Phase 4 both depend on Phase 2 and are independent of each other -- they could be reordered if needed.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Application Skeleton with Mocks | 2/3 | In progress | - |
| 2. Core Investigation Pipeline | 4/4 | Complete   | 2026-03-25 |
| 3. Classification and Verdict Engine | 1/2 | In Progress|  |
| 4. Cross-Platform Intelligence | 2/2 | Complete   | 2026-03-25 |
| 5. Event Scan Mode | 2/3 | In Progress|  |
