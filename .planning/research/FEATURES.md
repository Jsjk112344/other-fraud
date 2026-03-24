# Feature Research

**Domain:** Autonomous fraud intelligence agent for ticket marketplace scams (hackathon demo)
**Researched:** 2026-03-24
**Confidence:** HIGH

## Context: 6-Hour Solo Hackathon Constraints

Every feature decision must pass the "demo-ability" test: Can a judge understand this feature's value within 10 seconds of seeing it? Can a solo builder ship it in the time budget? The TinyFish hackathon judges care about **agentic web intelligence** -- the agent autonomously navigating real websites, gathering evidence, and reasoning. Features that showcase this win. Features that distract from this lose.

## Feature Landscape

### Table Stakes (Demo Fails Without These)

These are not negotiable. If any of these are missing or broken, the demo collapses.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| URL input and investigation trigger | The core interaction. User pastes a listing URL, agent starts working. Without this, there is no product. | LOW | Single text input + submit button. Must handle Carousell and Viagogo URLs at minimum. |
| Listing detail extraction via TinyFish | Agent must read the listing page: price, seller name, description, transfer method, event name. This is the first evidence signal. | MEDIUM | TinyFish navigates to URL, extracts structured data. Must handle anti-bot pages that Carousell uses. |
| Seller profile investigation | Agent navigates to the seller's profile page and extracts account age, total listings, ratings/reviews. This is what makes it an "investigation" not just a "scraper." | MEDIUM | Requires TinyFish to follow a link from listing to seller profile -- demonstrates autonomous navigation. |
| Real-time step streaming to UI via SSE | Judges must SEE the agent working. Each investigation step appears as it happens. Without this, the agent is a black box and the demo is a loading spinner. | MEDIUM | FastAPI SSE endpoint, React consuming EventSource. Each step is a discrete event with type, data, and timestamp. |
| Step-by-step evidence cards in UI | Each piece of gathered evidence renders as a visible card (listing details, seller info, price comparison, etc). The audience watches evidence accumulate. | MEDIUM | Cards appear one-by-one as SSE events arrive. Each card shows what the agent found and why it matters. |
| Final verdict with reasoning | Classification (LEGITIMATE / SCALPING_VIOLATION / LIKELY_SCAM / COUNTERFEIT_RISK) plus confidence score plus natural language explanation. The payoff of the investigation. | MEDIUM | OpenAI gpt-4o takes all gathered signals and produces structured verdict. Must feel authoritative, not vague. |
| Price comparison against official sources | Agent checks SISTIC/Ticketmaster for face value and sold-out status. This is the most immediately understandable fraud signal -- "listing is 5x face value" or "tickets never went on sale here." | MEDIUM | TinyFish navigates to official ticket site, extracts price/availability. Clear, objective signal. |

### Differentiators (What Wins the Hackathon)

These separate "impressive demo" from "yet another AI wrapper." Prioritize the top 3.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Cross-platform correlation | Agent searches the same event on OTHER marketplaces (Viagogo if input was Carousell, vice versa) and finds duplicates or suspicious patterns. This is the "multi-website autonomous agent" wow factor that demonstrates true agentic behavior across multiple sites. | HIGH | TinyFish navigates to a second marketplace, searches for same event, compares listings. Most impressive agent capability but also riskiest -- depends on search working reliably. |
| Signal-by-signal animated reveal | Evidence cards don't just appear -- they animate in with a visual narrative. Each signal has a color-coded risk indicator (green/yellow/red). The verdict "builds" visually as signals accumulate. Turns the investigation into a story. | LOW | CSS animations + conditional styling. High visual impact for minimal code. Prior project (ducket-ai) validated this pattern works for demos. |
| Rules engine for obvious cases | Extreme underpricing (80% below face value) or extreme markup (10x+) gets instant classification WITHOUT an LLM call. Shows sophistication -- the system is not just "throw everything at GPT." | LOW | Simple conditional logic before the LLM call. Fast, deterministic, impressive when explained. "We don't waste an LLM call on obvious scams." |
| Event scan mode | Instead of one listing, user enters an event name (e.g., "F1 Singapore Grand Prix") and the agent scans MULTIPLE listings across platforms. Produces a threat intelligence summary: total listings found, flagged count, estimated fraud exposure in dollars. | HIGH | Multiple TinyFish sessions in parallel (or sequential). Much more impressive than single-listing mode but 3-4x the implementation time. Build ONLY if single-listing mode works perfectly first. |
| Threat intelligence dashboard for event scan | Summary view: total listings scanned, fraud rate, dollar exposure, worst offenders. Turns FraudFish from a "checker" into an "intelligence platform." | MEDIUM | Depends entirely on event scan mode working. Aggregation UI over scan results. Only build if event scan ships. |
| Confidence calibration with validation layer | After LLM classifies, a validation layer checks for obvious mistakes (e.g., LLM says LEGITIMATE but price is 10x face value). Shows engineering rigor. | LOW | Simple post-processing rules. Catches LLM hallucination edge cases. Easy to implement, good talking point in demo. |

### Anti-Features (Do NOT Build in 6 Hours)

These seem appealing but will burn time without improving the demo.

| Feature | Why Tempting | Why Problematic | Alternative |
|---------|--------------|-----------------|-------------|
| User accounts and authentication | Feels "professional" | Zero demo value. Judges do not care about login screens. Burns 30-60 min on auth plumbing. | No auth. Public access. Paste URL and go. |
| PDF/downloadable report export | Seems like a "complete product" feature | Time sink for formatting, PDF generation library setup. Judges see the verdict on screen -- they do not need a PDF. | Show the verdict beautifully in the UI. Screenshot-worthy is enough. |
| Telegram group scraping | Third marketplace source, good for coverage story | Telegram groups are unstructured, require different parsing, may need Telegram API setup. High failure risk for marginal demo value. | Mention Telegram as "future expansion" in pitch. Focus on Carousell + Viagogo which are structured. |
| Historical investigation storage / database | "Save past investigations" sounds useful | Requires database setup, schema design, query UI. Zero value for a 3-minute demo where you run 1-2 investigations live. | Keep investigations in memory. Each demo run is fresh. |
| Blockchain/smart contract escrow | Trendy, sounds innovative | Explicitly out of scope per PROJECT.md. Not relevant to TinyFish judging criteria. Massive time sink. | Focus on detection and evidence, not enforcement. |
| Fine-tuned classification model | Better accuracy than prompt engineering | No time to train, no training data prepared. gpt-4o with good prompts + structured output is more than sufficient. | Prompt engineering + structured output + rules engine. |
| Multi-language support | Singapore is multilingual | UI translation is pure overhead for a demo. All demo content will be in English. | English only. Listing content is mostly English on Carousell/Viagogo anyway. |
| Automated takedown or reporting to authorities | "End-to-end solution" narrative | Way out of scope. Legal, ethical, and technical complexity. Demo is about detection, not enforcement. | Frame as "generates evidence for SPF or platform moderation teams." |
| Mobile responsive design | "Works everywhere" | Judges see it on a projector or laptop. Mobile CSS is wasted effort. | Desktop-optimized single-column layout. Looks great on a big screen. |
| Comprehensive error handling and retry logic | Production readiness | This is a demo, not production. If TinyFish fails, show a graceful "investigation incomplete" state and move to the next demo. Do not spend 2 hours on retry logic. | Basic try/catch, show error in UI, move on. Pre-test demo URLs to avoid failures. |

## Feature Dependencies

```
[URL Input]
    |
    v
[Listing Detail Extraction via TinyFish]
    |
    +---> [Seller Profile Investigation]
    |         |
    |         v
    |     (seller trust signals)
    |
    +---> [Price Comparison vs Official Sources]
    |         |
    |         v
    |     (pricing signals)
    |
    +---> [Cross-Platform Correlation] (DIFFERENTIATOR)
    |         |
    |         v
    |     (duplicate/pattern signals)
    |
    v
[Rules Engine] --obvious--> [Instant Verdict]
    |
    not obvious
    |
    v
[OpenAI gpt-4o Classification]
    |
    v
[Validation Layer]
    |
    v
[Final Verdict Display]

---

[Signal-by-Signal Animation] --enhances--> [Evidence Cards]
[Event Scan Mode] --requires--> [All Single-Listing Features Working]
[Threat Dashboard] --requires--> [Event Scan Mode]
```

### Dependency Notes

- **Cross-Platform Correlation requires Listing Extraction:** Must extract event name and seller info first to search on other platforms.
- **Event Scan Mode requires ALL single-listing features:** This is a multiplier on the core flow. If single-listing is broken, event scan amplifies the brokenness.
- **Threat Dashboard requires Event Scan:** Aggregation only makes sense with multiple scan results.
- **Rules Engine is independent of LLM:** Can be built and tested without OpenAI credits. Good pre-hackathon work.
- **Signal Animation enhances Evidence Cards:** Pure presentation layer, no backend dependency. Can be added last as polish.
- **Validation Layer enhances Classification:** Post-processing step, add after classification works.

## MVP Definition

### Hour 1-3: Core Investigation (Must Ship)

- [x] URL input triggers investigation
- [x] TinyFish extracts listing details (price, seller, event, description)
- [x] TinyFish navigates to seller profile and extracts trust signals
- [x] TinyFish checks official ticket site for face value
- [x] SSE streams each step to frontend in real-time
- [x] Evidence cards render as steps complete
- [x] Rules engine handles obvious over/underpricing
- [x] gpt-4o produces verdict with reasoning from all signals
- [x] Final verdict card with classification + confidence + explanation

### Hour 3-5: Differentiators (Should Ship)

- [ ] Cross-platform correlation (search same event on second marketplace)
- [ ] Signal-by-signal animated reveal with risk color coding
- [ ] Validation layer catches LLM classification mistakes
- [ ] Confidence calibration display

### Hour 5-6: Stretch Goals (Ship If Time Permits)

- [ ] Event scan mode (search by event name, investigate multiple listings)
- [ ] Threat intelligence summary for event scan
- [ ] Polish: loading states, transitions, professional styling

### Explicitly Deferred

- [ ] Telegram group scraping -- unstructured, high failure risk
- [ ] PDF reports -- zero demo value
- [ ] Database/persistence -- unnecessary for live demo
- [ ] Mobile responsive -- judges watch on desktop/projector

## Feature Prioritization Matrix

| Feature | Demo Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| URL input + investigation trigger | HIGH | LOW | P1 |
| Listing detail extraction | HIGH | MEDIUM | P1 |
| Seller profile investigation | HIGH | MEDIUM | P1 |
| Real-time SSE streaming | HIGH | MEDIUM | P1 |
| Evidence cards UI | HIGH | MEDIUM | P1 |
| Price comparison (official sources) | HIGH | MEDIUM | P1 |
| Final verdict with reasoning | HIGH | MEDIUM | P1 |
| Rules engine (obvious cases) | MEDIUM | LOW | P1 |
| Signal-by-signal animation | HIGH | LOW | P2 |
| Cross-platform correlation | HIGH | HIGH | P2 |
| Validation layer | MEDIUM | LOW | P2 |
| Event scan mode | HIGH | HIGH | P3 |
| Threat intelligence dashboard | MEDIUM | MEDIUM | P3 |

**Priority key:**
- P1: Must ship in hours 1-3 (core investigation flow)
- P2: Should ship in hours 3-5 (differentiators)
- P3: Stretch goals for hours 5-6 (impressive if achieved)

## Competitor Feature Analysis

| Feature | Enterprise Fraud Tools (Feedzai, SEON) | OSINT Agents (Blue Helix, Robin) | FraudFish Approach |
|---------|----------------------------------------|----------------------------------|-------------------|
| Data sources | Bank transactions, KYC, device fingerprints | Web pages, dark web, social media | Marketplace listings, seller profiles, official ticket sites |
| Detection method | ML models trained on historical fraud | LLM-driven analysis + search | Rules engine + LLM classification on gathered evidence |
| User interaction | Dashboard for fraud analysts | Query interface for researchers | Single URL input, zero configuration |
| Real-time visibility | Alert queues, batch processing | Report generation | Live streaming of investigation steps |
| Multi-source correlation | Cross-channel transaction linking | Cross-platform OSINT gathering | Cross-marketplace listing comparison |
| Time to result | Milliseconds (pre-trained models) | Minutes to hours | 30-60 seconds (autonomous investigation) |

**FraudFish's unique position:** It is not an enterprise fraud platform (too complex for demo) or a general OSINT tool (too broad). It is a focused, autonomous investigation agent for a specific, relatable problem (ticket scams) with a compelling visual narrative (watch the agent work). This focus is its strength for a hackathon.

## Demo Script Alignment

The features are designed to produce this 3-minute demo flow:

1. **0:00-0:30** -- Problem statement: "2,700 victims, S$1.6M lost to ticket scams in Singapore"
2. **0:30-1:00** -- Paste a Carousell F1 GP listing URL, hit Investigate
3. **1:00-2:00** -- Watch evidence cards stream in: listing details, seller profile, official price check, cross-platform search
4. **2:00-2:30** -- Verdict reveals with reasoning: "LIKELY_SCAM -- seller account is 3 days old, price is 40% below face value, no reviews, listing duplicated on Viagogo"
5. **2:30-3:00** -- (If event scan shipped) Show event-wide scan: "47 F1 GP listings found, 12 flagged, S$38K estimated fraud exposure"

Every P1 feature maps to steps 2-4. P2 features enrich step 4. P3 features enable step 5.

## Sources

- [DataDome: How AI Is Used in Fraud Detection](https://datadome.co/learning-center/ai-fraud-detection/)
- [Ravelin: Ticketing Fraud Types and Signals](https://www.ravelin.com/blog/ticketing-fraud)
- [Infoblox: Blue Helix Agentic OSINT Researcher](https://www.infoblox.com/blog/security/blue-helix-agentic-osint-researcher/)
- [OWASP Social OSINT Agent](https://owasp.org/www-project-social-osint-agent/)
- [Microsoft AI Agents Hackathon 2025 Judging Criteria](https://microsoft.github.io/AI_Agents_Hackathon/)
- [Kong Agentic AI Hackathon Winners 2025](https://konghq.com/blog/news/winners-of-kong-agentic-ai-hackathon)
- [AG-UI Protocol for Real-Time Agent Streaming](https://docs.ag-ui.com/introduction)
- [Etix: Fighting Ticket Fraud 101](https://hello.etix.com/product-spotlight-fighting-ticket-fraud-101/)
- [FraudNet: Best Fraud Detection Tools for Online Marketplaces](https://www.fraud.net/resources/best-fraud-detection-tools-for-online-marketplaces)
- PROJECT.md prior work section (ducket-ai-galactica validated signal-by-signal reveal pattern)

---
*Feature research for: Autonomous fraud intelligence agent (FraudFish)*
*Researched: 2026-03-24*
