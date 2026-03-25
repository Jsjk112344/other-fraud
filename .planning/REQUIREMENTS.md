# Requirements: FraudFish

**Defined:** 2026-03-24
**Core Value:** The agent must autonomously investigate a listing across multiple web sources and produce a verdict with visible evidence — not just a score, but proof the audience can see being gathered in real-time.

## v1 Requirements

Requirements for hackathon submission (March 28, 2026).

### Investigation Pipeline

- [x] **PIPE-01**: User can paste a Carousell/Viagogo listing URL into an input field and trigger an investigation
- [x] **PIPE-02**: Agent extracts listing details (price, seller name, description, transfer method, posting date) from the URL via TinyFish
- [x] **PIPE-03**: Agent navigates to the seller's profile page via TinyFish and extracts account age, total listings, listing categories, and review text/sentiment
- [x] **PIPE-04**: Agent checks official ticket sites (SISTIC, Ticketmaster SG, F1 official) via TinyFish for event existence, face value, and sold-out status
- [ ] **PIPE-05**: Agent scans 10+ other listings for the same event across platforms via TinyFish to calculate market rate and detect statistical outliers
- [ ] **PIPE-06**: Agent searches other marketplaces for the same seller name or listing text via TinyFish to detect cross-platform duplicates
- [ ] **PIPE-07**: Investigation steps run in parallel where independent (asyncio.gather) to complete within 60 seconds total
- [x] **PIPE-08**: Cached/fallback data exists for each investigation step so the demo functions even if TinyFish is slow or blocked

### Classification

- [ ] **CLAS-01**: Rules engine classifies obvious cases (extreme underpricing < -40% face = LIKELY_SCAM, extreme markup > 300% on non-sold-out = SCALPING_VIOLATION) without an LLM call
- [ ] **CLAS-02**: OpenAI gpt-4o classifies ambiguous cases using full evidence from all investigation steps, returning structured JSON with category, confidence, and natural language reasoning
- [x] **CLAS-03**: Four classification categories: LEGITIMATE, SCALPING_VIOLATION, LIKELY_SCAM, COUNTERFEIT_RISK
- [ ] **CLAS-04**: Validation layer catches obvious LLM mistakes (e.g., calling extreme underpricing LEGITIMATE)
- [x] **CLAS-05**: Confidence score (0-100%) is calculated with enforcement gate at configurable threshold

### Real-Time Streaming UI

- [x] **RTUI-01**: Backend streams investigation progress to frontend via Server-Sent Events (SSE) from FastAPI
- [x] **RTUI-02**: Frontend consumes SSE via fetch + ReadableStream (POST-based SSE, not EventSource)
- [x] **RTUI-03**: Six investigation steps displayed as timeline cards: Extracting Listing Data, Investigating Seller Profile, Verifying Event Details, Checking Market Rates, Cross-Platform Search, Synthesizing Verdict
- [x] **RTUI-04**: Each step transitions through states: PENDING → ACTIVE (with progress indicator) → COMPLETE (with extracted data) or ERROR
- [x] **RTUI-05**: Signal-by-signal animated reveal with staggered entrance animations on step completion
- [ ] **RTUI-06**: Final verdict panel displays category (color-coded), confidence score, and expandable natural language reasoning
- [ ] **RTUI-07**: Five risk indicator meters (Pricing Anomaly, Seller Reputation, Event Verification, Cross-Platform Duplicates, Listing Authenticity) with severity bars
- [ ] **RTUI-08**: Evidence sidebar shows seller summary, price comparison bar chart, and listing data
- [x] **RTUI-09**: All UI follows the FraudFish DESIGN.md design system (colors, fonts, components, animations, layout)

### Event Scan Mode

- [ ] **SCAN-01**: User can enter an event name to trigger a batch scan across multiple marketplaces
- [ ] **SCAN-02**: Agent searches Carousell and Viagogo for listings matching the event via TinyFish
- [ ] **SCAN-03**: Agent runs investigation pipeline on each discovered listing
- [ ] **SCAN-04**: Threat intelligence summary displays: total listings found, flagged suspicious count, confirmed likely scam count, estimated fraud exposure in SGD

## v2 Requirements

Deferred to post-hackathon.

### Enhanced Intelligence

- **INTL-01**: Telegram group monitoring for migrated listings
- **INTL-02**: Downloadable PDF evidence report
- **INTL-03**: Historical seller tracking across investigations
- **INTL-04**: Image/screenshot analysis for fake ticket detection

### Scale

- **SCAL-01**: Scheduled periodic scans (sentry mode)
- **SCAL-02**: Database persistence for investigation history
- **SCAL-03**: User accounts and saved investigations
- **SCAL-04**: API access for third-party integration

## Out of Scope

| Feature | Reason |
|---------|--------|
| Blockchain/escrow/smart contracts | Not relevant to TinyFish hackathon judging criteria |
| User authentication/accounts | Zero demo value for a solo hackathon build |
| Database persistence | Investigations are ephemeral, no storage needed for demo |
| Mobile responsive design | Desktop demo only at hackathon (though DESIGN.md has mobile specs for later) |
| Telegram scraping | High complexity, less structured data, defer to v2 |
| PDF report generation | Visual UI verdict is the demo — export is v2 polish |
| Automated enforcement/takedowns | Detection and evidence only |
| Model training/fine-tuning | Prompt engineering + structured output only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIPE-01 | Phase 1 | Complete |
| PIPE-02 | Phase 2 | Complete |
| PIPE-03 | Phase 2 | Complete |
| PIPE-04 | Phase 2 | Complete |
| PIPE-05 | Phase 4 | Pending |
| PIPE-06 | Phase 4 | Pending |
| PIPE-07 | Phase 2 | Pending |
| PIPE-08 | Phase 1 | Complete |
| CLAS-01 | Phase 3 | Pending |
| CLAS-02 | Phase 3 | Pending |
| CLAS-03 | Phase 1 | Complete |
| CLAS-04 | Phase 3 | Pending |
| CLAS-05 | Phase 1 | Complete |
| RTUI-01 | Phase 1 | Complete |
| RTUI-02 | Phase 1 | Complete |
| RTUI-03 | Phase 1 | Complete |
| RTUI-04 | Phase 1 | Complete |
| RTUI-05 | Phase 1 | Complete |
| RTUI-06 | Phase 1 | Pending |
| RTUI-07 | Phase 1 | Pending |
| RTUI-08 | Phase 1 | Pending |
| RTUI-09 | Phase 1 | Complete |
| SCAN-01 | Phase 5 | Pending |
| SCAN-02 | Phase 5 | Pending |
| SCAN-03 | Phase 5 | Pending |
| SCAN-04 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 26 total
- Mapped to phases: 26
- Unmapped: 0

---
*Requirements defined: 2026-03-24*
*Last updated: 2026-03-24 after roadmap creation*
