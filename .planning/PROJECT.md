# FraudFish

## What This Is

FraudFish is an autonomous fraud intelligence agent that investigates suspicious ticket listings on secondary marketplaces in Singapore. Users paste a listing URL (Carousell, Viagogo, Telegram) and the agent autonomously navigates multiple websites — seller profiles, official ticket sites, other marketplaces — to build an evidence-backed fraud verdict in under 60 seconds. Built for the TinyFish SG Hackathon (March 28, 2026).

## Core Value

The agent must autonomously investigate a listing across multiple web sources and produce a verdict with visible evidence — not just a score, but proof the audience can see being gathered in real-time.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User can paste a Carousell/Viagogo listing URL and trigger an investigation
- [ ] Agent extracts listing details (price, seller, description, transfer method) via TinyFish
- [ ] Agent navigates to seller's profile page and extracts account age, listing history, and reviews via TinyFish
- [ ] Agent checks official ticket sites (SISTIC, Ticketmaster SG, F1 official) for real face value and sold-out status via TinyFish
- [ ] Agent searches other marketplaces for the same listing/seller to detect cross-platform duplicates via TinyFish
- [ ] Agent calculates market rate by scanning other listings for the same event via TinyFish
- [ ] OpenAI gpt-4o synthesizes all gathered evidence into a reasoned classification (LEGITIMATE, SCALPING_VIOLATION, LIKELY_SCAM, COUNTERFEIT_RISK)
- [ ] Rules engine handles obvious cases (extreme underpricing, extreme markup) without LLM call
- [ ] Validation layer catches obvious LLM classification mistakes
- [ ] Investigation steps stream to the UI in real-time via SSE
- [ ] Each investigation step is visible as a discrete card/signal in the UI
- [ ] Signal-by-signal animated reveal shows evidence building toward verdict
- [ ] Final verdict displays category, confidence score, and natural language reasoning
- [ ] Event scan mode: user enters event name, agent searches all platforms and investigates multiple listings
- [ ] Threat intelligence summary for event scan: total listings, flagged count, estimated fraud exposure

### Out of Scope

- Blockchain/smart contracts/escrow — not relevant to TinyFish hackathon judging
- Mobile app — web dashboard only
- User accounts/auth — no login, just paste and investigate
- Downloadable PDF reports — visual UI verdict only (may add if time permits)
- Automated enforcement/takedowns — detection and evidence only
- Training/fine-tuning models — prompt engineering + structured output only

## Context

### The Problem

In 2024-2025, Singapore saw 2,700+ victims of concert ticket scams with S$1.6M+ in losses. Ticket scalping is not illegal in Singapore — there is no anti-scalping legislation. Enforcement is reactive: SPF issues advisories after scams happen, Carousell bans listings after police request. When Carousell bans listings, scammers migrate to Telegram, Xiaohongshu, and Facebook where there is less moderation.

Manual scam detection takes hours. In that time, fans have already lost money. Police are understaffed and have bigger issues. FraudFish is proactive detection — an AI agent that investigates like a human fraud analyst, but in 30 seconds instead of 30 minutes.

### Demo Events (March 28, 2026)

**Hero event:** F1 Singapore Grand Prix (Oct 9-11, 2026) — tickets already on sale, $3K+ face values, perennial scalping target, Singapore iconic event.

**Breadth events** (showing scale across multiple events):
- DAY6 10th Anniversary (April 18, 2026) — K-pop, 3 weeks away
- (G)I-DLE Syncopation (June 13, 2026) — K-pop, high demand
- Eric Chou (April 11-12, 2026) — Mandopop, strong demand
- IVE Show What I Am (May 9, 2026) — K-pop

K-pop events dominate fraud statistics because they sell out instantly, have young fanbases, often have non-transferable tickets (making all resale inherently suspect), and trigger extreme emotional urgency.

### Key Statistics for Pitch

- 2024: 2,000+ victims, S$1M+ losses (Jan-May alone)
- 2025: 722 cases, S$615,000 losses (Jan-Oct)
- BLACKPINK 2025: S$26,000 lost in just 2 weeks
- Carousell 2024: blocked 1.28M phishing links, suspended 422K accounts
- No anti-scalping law in Singapore — enforcement gap FraudFish fills

### Target Marketplaces

1. **Carousell SG** — #1 peer marketplace in SG, where most scams happen, anti-bot protected
2. **Viagogo** — global resale platform, good for cross-platform correlation, anti-bot protected
3. **Telegram groups** — where listings migrate after Carousell bans, less structured

### Prior Work

Previous project (ducket-ai-galactica) built a similar concept with OpenClaw + Patchright + Claude + Solidity escrow. Key reusable patterns:
- 5-signal weighted risk engine (pricing, seller trust, listing quality, temporal pattern, platform trust)
- Two-tier classification (rules for obvious cases, LLM for ambiguous)
- Multi-marketplace parallel scraping with fallback chains
- Signal-by-signal animated reveal UI

This project rebuilds from scratch using TinyFish + OpenAI, dropping blockchain, and focusing on the investigation pipeline as the core innovation.

## Constraints

- **Timeline**: 6 hours hacking window (10:30 AM - 4:30 PM, hard code freeze March 28, 2026)
- **Team**: Solo builder
- **Required tech**: TinyFish APIs for all web interaction, OpenAI models for classification
- **API credits**: Provided at hackathon, not available beforehand — all pre-work must be mockable/testable without live API calls
- **No commits until Saturday**: Repo initialized on hackathon day. Pre-work is code ready to deploy, not committed
- **Submission**: GitHub repo + live demo (3-5 minutes)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python + FastAPI backend | TinyFish has first-class Python SDK, FastAPI has native SSE, solo builder needs speed | — Pending |
| React + Vite frontend | Lightweight, fast to build, sufficient for investigation UI | — Pending |
| OpenAI gpt-4o for classification | Hackathon sponsor, free credits, strong structured output | — Pending |
| Drop blockchain/escrow | TinyFish judges care about web agent intelligence, not Web3 | — Pending |
| Investigation over classification | Multi-step evidence gathering impresses more than a scoring checklist | — Pending |
| F1 GP as hero demo event | High face values, everyone in SG knows it, active listings now | — Pending |
| Carousell + Viagogo + Telegram | Covers #1 scam platform + cross-platform correlation + migration destination | — Pending |

---
*Last updated: 2026-03-24 after initialization*
