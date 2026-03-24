# Pitfalls Research

**Domain:** Autonomous fraud intelligence agent (hackathon web agent with TinyFish + OpenAI)
**Researched:** 2026-03-24
**Confidence:** MEDIUM-HIGH (TinyFish docs are sparse on error handling; OpenAI structured output pitfalls well-documented; hackathon patterns well-known)

## Critical Pitfalls

### Pitfall 1: TinyFish Agent Calls Take 15-45 Seconds Each, Blowing the 60-Second Budget

**What goes wrong:**
Each TinyFish `run-sse` call spins up a headless browser, navigates to a page, interprets the goal with an LLM, and extracts data. This is not a fast API call -- it is an autonomous browser session. A single investigation requires 4-6 TinyFish calls (listing page, seller profile, official ticket site, other marketplace, market rate scan). If these run sequentially, a single investigation takes 90-270 seconds, far exceeding the promised "under 60 seconds" and killing the live demo pacing.

**Why it happens:**
Developers think of TinyFish like a REST API and chain calls sequentially. The SSE streaming creates an illusion of speed (events are flowing), but the total wall-clock time is the sum of all calls.

**How to avoid:**
- Run independent TinyFish calls in parallel using `asyncio.gather()`. The listing extraction must happen first (to get seller name, event name, price), but the seller profile check, official site check, and marketplace scan can all run concurrently after that.
- Design the investigation as a dependency graph: Phase 1 (listing extraction) -> Phase 2 (3-4 parallel calls using extracted data) -> Phase 3 (OpenAI synthesis).
- Set a hard timeout of 20 seconds per TinyFish call. If a call does not complete, use whatever partial data arrived and mark that signal as "inconclusive."
- Pre-test exact goal prompts for each target site to minimize TinyFish's navigation time.

**Warning signs:**
- Investigation taking more than 30 seconds in testing.
- SSE stream going quiet for long periods between signals.
- TinyFish calls returning COMPLETE events with empty or wrong data (agent got lost navigating).

**Phase to address:**
Phase 1 (Core Pipeline) -- the parallel execution architecture must be designed from the start, not bolted on later.

---

### Pitfall 2: Carousell's Cloudflare Protection Blocks TinyFish During Live Demo

**What goes wrong:**
Carousell uses Cloudflare Enterprise Bot Management with per-customer ML models, WAF rules, TLS fingerprinting, JavaScript challenges, and Turnstile CAPTCHA. Even with TinyFish's `browser_profile: "stealth"` mode, Cloudflare may detect the automated browser session and serve a challenge page or block the request entirely. This is catastrophic during a live demo -- the hero use case fails in front of judges.

**Why it happens:**
Developers test against a site 5-10 times during development and it works. But Cloudflare's detection is probabilistic and adaptive -- it may work 8 out of 10 times and fail the 2 times that matter (demo day, different IP, different fingerprint). Hackathon venue WiFi has a shared IP that may already be flagged from other participants' scraping attempts.

**How to avoid:**
- Always use `browser_profile: "stealth"` and `proxy_config: { enabled: true, country_code: "SG" }` for Carousell calls.
- Build a fallback chain: TinyFish stealth -> TinyFish with proxy -> cached/pre-scraped data. Never let a single point of failure kill the demo.
- Pre-scrape 3-5 real listings the morning of the hackathon and store them as JSON fixtures. If live scraping fails during demo, seamlessly fall back to cached data with a small UI indicator ("cached data" vs "live").
- Have Viagogo as an alternate hero demo target -- it is a more structured site that may be easier to scrape reliably.
- Test from the hackathon venue WiFi during setup time, not just from home.

**Warning signs:**
- TinyFish returning HTML containing "Checking your browser" or Cloudflare challenge page content instead of listing data.
- Inconsistent results -- same URL works sometimes but not others.
- TinyFish COMPLETE event with status but empty/garbage resultJson.

**Phase to address:**
Phase 1 (Core Pipeline) for the fallback architecture. Phase 3 (Demo Hardening) for the cached fixtures and demo-day resilience testing.

---

### Pitfall 3: OpenAI Structured Output Schema Rejected at Runtime

**What goes wrong:**
OpenAI's structured outputs with `strict: true` require `additionalProperties: false` on every object in the schema, all fields must be in the `required` array (no truly optional fields), no `$ref` or recursive schemas, no Pydantic `Field` constraints like `min_length` or `ge`, and no `Dict` types. If your Pydantic model uses any of these common patterns, the API call fails with a 400 error at runtime -- not at import time, not during testing without the API, but the first time you actually call OpenAI with that schema.

**Why it happens:**
Developers write clean Pydantic models with optional fields, validation constraints, and nested types during pre-work. These models work perfectly for local testing and type checking. But OpenAI's "Structured Outputs" supports only a tiny subset of JSON Schema, and the incompatibility only surfaces when you make a real API call. Since hackathon API credits are not available until day-of, this is a day-of surprise.

**How to avoid:**
- Make every field required. Use `Optional[str]` (which becomes `type: ["string", "null"]`) for fields that might not have data -- the model returns `null` instead of omitting the field.
- Never use `Field(min_length=..., ge=..., description=...)` validators in models destined for OpenAI. Use plain type annotations only.
- Avoid `Dict[str, Any]` -- OpenAI cannot handle arbitrary dictionary types. Use explicit nested models instead.
- Test schema compatibility before hackathon day: call `openai.pydantic_function_tool(YourModel)` or use `model_json_schema()` and manually verify it meets OpenAI's constraints. This does not require API credits.
- Keep the verdict schema flat and simple: `classification` (enum), `confidence` (float), `reasoning` (str), `signals` (list of signal objects). No fancy nesting.

**Warning signs:**
- Pydantic models with `Optional` fields not wrapped in the union-with-null pattern.
- Any use of `Field()` with validation parameters.
- Nested models more than 2 levels deep.
- `Dict` or `Any` types anywhere in the schema.

**Phase to address:**
Phase 1 (Core Pipeline) -- define and validate the OpenAI response schemas before writing any classification logic.

---

### Pitfall 4: SSE Stream Appears Frozen to the User (Buffering, CORS, No Heartbeat)

**What goes wrong:**
The FastAPI backend sends SSE events, but the React frontend receives them in large batches instead of real-time, or does not receive them at all. The investigation appears to hang for 30+ seconds, then all signals dump at once. This destroys the "watch the agent investigate in real-time" experience that is the core demo value.

**Why it happens:**
Three common causes: (1) A reverse proxy (nginx, Vercel, or even the browser) buffers the SSE stream and delivers it in chunks. (2) CORS headers are missing or misconfigured, so the EventSource connection silently fails. (3) There is no heartbeat/keep-alive, so the connection drops after an idle period and the browser auto-reconnects, losing state.

**How to avoid:**
- Set these headers on every SSE response: `Cache-Control: no-cache`, `X-Accel-Buffering: no`, `Connection: keep-alive`.
- Send a heartbeat comment (`: heartbeat\n\n`) every 5 seconds during long TinyFish operations so the connection stays alive and the user sees the stream is active.
- Use `sse-starlette` package (not raw StreamingResponse) -- it handles SSE formatting correctly and supports proper event types.
- For CORS, use FastAPI's `CORSMiddleware` with `allow_origins=["*"]` during development. Test the SSE connection from the React app early, not as a final integration step.
- During demo, run frontend and backend on the same machine/port (serve React static files from FastAPI) to eliminate CORS entirely.

**Warning signs:**
- `curl -N` to the SSE endpoint shows events arriving in batches instead of one-by-one.
- Browser DevTools Network tab shows the EventSource request as "pending" with no data flowing.
- Events arrive but `event.data` is undefined or malformed.

**Phase to address:**
Phase 1 (Core Pipeline) -- SSE must be the first integration tested, not the last. Build a dummy SSE endpoint that sends fake signals before any TinyFish integration.

---

### Pitfall 5: Solo Builder Spends 4 of 6 Hours on Plumbing, Not Demo-Worthy Features

**What goes wrong:**
The 6-hour window evaporates on: debugging TinyFish API authentication (30 min), fighting CORS (30 min), fixing SSE buffering (30 min), wrestling with OpenAI schema errors (30 min), setting up React project (30 min), deploying for demo (30 min). That is 3 hours of plumbing, leaving only 3 hours for the actual investigation logic, UI polish, and demo prep. The result is a technically functional but visually unimpressive demo that does not showcase the investigation intelligence.

**Why it happens:**
Hackathon builders underestimate integration overhead and overestimate how much code they have pre-written. Every integration boundary (TinyFish <-> Backend, Backend <-> Frontend, Frontend <-> SSE) is a potential 30-60 minute debugging session.

**How to avoid:**
- Pre-build everything possible before hackathon day. The constraint is "no commits until Saturday" -- not "no code until Saturday." Have the full application skeleton ready to copy-paste:
  - FastAPI app with SSE endpoint, CORS configured, health check.
  - React app with SSE consumer, signal card components, verdict display.
  - Pydantic models for TinyFish responses and OpenAI schemas (pre-validated).
  - Mock data that exercises the full pipeline without any API calls.
- Time-box ruthlessly on hackathon day: first 90 min = get live TinyFish calls working. Next 90 min = get OpenAI classification working. Next 90 min = polish UI and demo flow. Final 90 min = demo prep, fallback testing, pitch practice.
- If any single task exceeds its time box, skip it and use the mock/fallback. A working demo with cached data beats a broken demo with live scraping.

**Warning signs:**
- Still debugging infrastructure at the 2-hour mark.
- No working end-to-end flow (even with mocks) by the 3-hour mark.
- Adding new features in the final 90 minutes instead of polishing existing ones.

**Phase to address:**
Phase 0 (Pre-work) -- the entire application skeleton, mocks, and fallback system must exist before hackathon day.

---

### Pitfall 6: TinyFish Goal Prompt Returns Wrong or Partial Data

**What goes wrong:**
TinyFish's natural language goal is powerful but unpredictable. A goal like "extract the listing price and seller name" might return the wrong price (shipping cost instead of item price), miss fields entirely, or navigate to the wrong page. On Carousell, where listing pages have dynamic rendering and multiple price displays (original price, offer price, "make offer" button), the agent may grab the wrong element.

**Why it happens:**
TinyFish uses an LLM to interpret the goal and decide what to extract. Different page layouts, A/B tests, and dynamic content can confuse the agent. The goal prompt that worked on Monday's listing may fail on Friday's listing because Carousell changed their layout.

**How to avoid:**
- Write hyper-specific goal prompts that describe exactly what to extract and where: "Extract the listing title, the asking price shown below the title (not the 'Make Offer' price), the seller username shown in the seller info card, and the item description text" rather than "get listing details."
- Specify the exact JSON schema you want returned in the goal prompt: "Return as JSON with fields: title (string), price_sgd (number), seller_username (string), description (string)."
- Build a validation layer that checks TinyFish results: Is the price a reasonable number? Is the seller name non-empty? If validation fails, retry once with a more specific goal prompt, then fall back to partial data.
- Test goal prompts against 5+ different real listings for each target site. Save the prompts that work as constants, not as dynamically generated strings.

**Warning signs:**
- TinyFish returns null or empty for fields you expected.
- Prices come back as strings with currency symbols instead of numbers.
- Seller name returns "null" or the site name instead of the actual seller.
- Results are inconsistent across different listings on the same site.

**Phase to address:**
Phase 1 (Core Pipeline) -- goal prompts must be iterated and hardened for each target marketplace.

---

### Pitfall 7: Demo Crashes Because Investigation Hits an Unhandled Edge Case

**What goes wrong:**
During the live demo, the judge suggests a URL the builder has never tested. The listing is deleted, the seller profile is private, the event is in a language other than English, or the price format is unexpected. The application throws an unhandled exception and the demo dies on stage.

**Why it happens:**
Builders test the happy path 20 times and never test failure cases. Web data is messy -- deleted listings, private profiles, rate-limited pages, and unexpected formats are the norm, not the exception.

**How to avoid:**
- Wrap every TinyFish call and OpenAI call in try/except with graceful degradation. A failed signal should produce a "Could not verify" card in the UI, not a crash.
- Pre-select 2-3 demo URLs that you have tested extensively. Steer the demo toward these URLs. Have a "let me show you this interesting case" pivot ready if a judge's URL fails.
- Build an explicit error state for each signal: "Seller profile: Unable to access (account may be private)." This actually looks more intelligent than crashing -- real fraud analysts encounter access limitations too.
- Test with: deleted listing URL, private seller profile, listing in Chinese, listing with no price, listing from an unsupported platform.

**Warning signs:**
- Any uncaught exception in the investigation pipeline.
- No error UI states designed for any component.
- Only tested with 1-2 known-good URLs.

**Phase to address:**
Phase 2 (Intelligence Layer) for error handling in classification logic. Phase 3 (Demo Hardening) for comprehensive edge case testing and demo URL selection.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded goal prompts per site | Fast to implement, reliable | Cannot handle new marketplaces without code changes | Always acceptable for hackathon -- 3 target sites is the scope |
| No database, all in-memory | Zero setup time | Investigations vanish on restart, no historical analysis | Always acceptable for hackathon -- demo only needs to run once |
| `allow_origins=["*"]` CORS | Eliminates CORS debugging | Security issue in production | Always acceptable for hackathon -- no auth, no user data |
| Synchronous OpenAI calls (not streaming) | Simpler code, easier error handling | Verdict appears all-at-once instead of streaming reasoning | Acceptable if time-boxed -- stream the investigation steps, batch the verdict |
| Pre-cached fallback data mixed with live results | Ensures demo never fails | Misleading if not disclosed | Acceptable only if UI indicates "cached" vs "live" |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| TinyFish SSE | Parsing the entire SSE stream as one JSON blob | Process each `data:` line individually, look for event with `type == "COMPLETE"` and `status == "COMPLETED"`, extract `resultJson` field |
| TinyFish SSE | Not handling non-COMPLETE events | Stream includes progress events (navigation steps, page loads). Forward these to the frontend as investigation step updates for visual feedback |
| TinyFish API | Using `browser_profile: "lite"` for Carousell/Viagogo | Always use `browser_profile: "stealth"` for bot-protected sites. Lite mode will be detected and blocked |
| OpenAI Structured Output | Using `Optional[field]` in Pydantic model | All fields must be `required`. Use `field: Optional[str] = None` with the type union pattern so the field is in `required` array but can be null |
| OpenAI Structured Output | Including Pydantic `Field()` validators | OpenAI does not support `min_length`, `ge`, `le`, `regex` constraints. Use plain type annotations only |
| FastAPI SSE | Using raw `StreamingResponse` for SSE | Use `sse-starlette` package which handles event formatting, keep-alive, and proper content-type headers |
| React EventSource | Not handling reconnection | EventSource auto-reconnects on disconnect. Use `fetch` with ReadableStream instead for single-shot SSE streams (investigations are not persistent connections) |

## Performance Traps

Patterns that work at small scale but fail during demo.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Sequential TinyFish calls | Investigation takes 2+ minutes | Parallelize with `asyncio.gather()` after initial listing extraction | Immediately -- first demo attempt |
| No timeout on TinyFish calls | UI hangs indefinitely if agent gets stuck navigating | Set 20-second timeout per call, degrade gracefully | When TinyFish encounters unexpected page state |
| OpenAI call with massive context | Classification takes 10+ seconds, costs excessive tokens | Summarize each signal to 2-3 sentences before sending to OpenAI, not raw scraped HTML | When passing full page content instead of extracted signals |
| No SSE heartbeat | Connection drops during long TinyFish operations, browser reconnects, duplicate signals appear | Send `: heartbeat\n\n` every 5 seconds | After ~30 seconds of no data on some browsers/proxies |

## Security Mistakes

Domain-specific security issues for this project.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Passing user-supplied URL directly to TinyFish without validation | SSRF -- user could scrape internal network addresses through TinyFish | Validate URL scheme (https only), validate domain against allowlist (carousell.sg, viagogo.com, etc.) |
| Exposing TinyFish/OpenAI API keys in frontend code | Key theft, credit exhaustion | Keys stay server-side only. Frontend talks to FastAPI backend, backend talks to APIs |
| Logging full scraped page content | May contain PII from seller profiles | Log only extracted structured data, not raw HTML |

## UX Pitfalls

Common user experience mistakes in fraud detection demos.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing a loading spinner for 60 seconds | Judges lose interest, assume it is broken | Stream each investigation step as it completes -- the progressive reveal IS the demo |
| Binary "SCAM / NOT SCAM" verdict | Feels like a coin flip, not intelligent | Use 4-tier classification (LEGITIMATE, SCALPING_VIOLATION, LIKELY_SCAM, COUNTERFEIT_RISK) with confidence score and reasoning |
| Showing raw JSON data | Looks like a developer tool, not a product | Each signal should be a visual card with an icon, title, value, and risk indicator (green/yellow/red) |
| No explanation of WHY a verdict was reached | Judges cannot evaluate if the AI is correct | Show the evidence chain: "Price is 340% above face value (S$1,200 vs S$350 official). Seller account is 3 days old. No other listings. Similar listing found on Viagogo at S$800." |
| Investigation steps all appear at once | Loses the "watch the agent work" magic | Animate signal cards appearing one-by-one with a slight delay. Use SSE timestamps to create natural pacing |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **SSE streaming:** Works in development but not through any proxy/CDN -- verify with `curl -N` from a different machine
- [ ] **TinyFish stealth mode:** Works from home WiFi but not from hackathon venue -- test from venue network during setup
- [ ] **OpenAI schema:** Pydantic model validates locally but OpenAI rejects it -- call `openai.pydantic_function_tool(Model)` to verify compatibility
- [ ] **Error handling:** Happy path works but any TinyFish failure crashes the app -- test with invalid URL, deleted listing, blocked site
- [ ] **Demo URLs:** Picked URLs that work today, but listings can be deleted/modified by demo day -- verify URLs morning-of and have 3 backups per demo scenario
- [ ] **Event scan mode:** Single investigation works but event scan triggers 5x parallel investigations that overwhelm rate limits -- test batch scenario
- [ ] **Verdict reasoning:** Classification works but reasoning is generic ("this looks suspicious") -- verify OpenAI produces specific, evidence-citing explanations
- [ ] **Mobile viewport:** Presenter laptop may connect to projector at different resolution -- verify UI is readable at 1024x768

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| TinyFish blocked by Cloudflare | LOW | Switch to cached fallback data. Say "the agent has cached results from earlier reconnaissance" -- this is actually how real intelligence tools work |
| OpenAI schema error | MEDIUM | Remove `strict: true`, use basic `response_format: { type: "json_object" }` with manual parsing. Less reliable but works immediately |
| SSE not streaming to frontend | MEDIUM | Fall back to polling: frontend calls `/api/investigation/{id}/status` every 2 seconds. Less elegant but functional |
| Demo URL is dead/changed | LOW | Pivot to backup URL. Say "let me show you a more interesting case" -- judges will not notice |
| Full pipeline crash during demo | HIGH | Have a pre-recorded 30-second screen capture of a successful investigation. "Let me show you what this looks like in action while I debug" -- then fix and do it live |
| Time runs out, features incomplete | MEDIUM | Cut event scan mode entirely. A polished single-investigation demo beats a buggy multi-investigation demo every time |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Sequential TinyFish calls (too slow) | Phase 0 (Pre-work architecture design) | Investigation completes in under 60 seconds with parallel calls |
| Carousell Cloudflare blocking | Phase 1 (Core Pipeline) + Phase 3 (Demo Hardening) | Successful scrape from hackathon venue WiFi with stealth+proxy |
| OpenAI schema incompatibility | Phase 0 (Pre-work schema validation) | `openai.pydantic_function_tool()` succeeds for all models |
| SSE buffering/CORS failures | Phase 1 (Core Pipeline) | Frontend receives events one-by-one in real-time from separate origin |
| Solo builder time waste | Phase 0 (Pre-work skeleton) | Full mock pipeline runs end-to-end before hackathon day |
| TinyFish goal prompt failures | Phase 1 (Core Pipeline) | 5+ different real listings successfully extracted per target site |
| Unhandled edge cases in demo | Phase 3 (Demo Hardening) | Tested with deleted, private, foreign-language, and no-price listings |
| API credits exhausted | Phase 1 (Core Pipeline) | Implemented caching layer so repeated investigations of same URL do not re-call APIs |

## Sources

- [TinyFish Web Agent Documentation](https://docs.tinyfish.ai) -- API endpoints, SSE format, stealth mode
- [TinyFish Scraping Examples](https://docs.tinyfish.ai/examples/scraping) -- goal-based extraction patterns
- [TinyFish LLMs.txt](https://docs.tinyfish.ai/llms.txt) -- sync/async/SSE/batch endpoints, cancellation limits
- [Cloudflare Carousell Case Study](https://www.cloudflare.com/case-studies/carousell/) -- confirms Carousell uses Cloudflare Enterprise
- [OpenAI Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs) -- schema constraints, all-fields-required rule
- [OpenAI Community: Structured Outputs Not Reliable](https://community.openai.com/t/structured-outputs-not-reliable-with-gpt-4o-mini-and-gpt-4o/918735) -- reliability issues
- [OpenAI Community: Schema additionalProperties](https://community.openai.com/t/schema-additionalproperties-must-be-false-when-strict-is-true/929996) -- strict mode constraints
- [OpenAI Community: Strict=True and Required Fields](https://community.openai.com/t/strict-true-and-required-fields/1131075) -- all fields must be required
- [FastAPI SSE Tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/) -- official SSE guidance
- [FastAPI SSE Client Disconnection Discussion](https://github.com/fastapi/fastapi/discussions/7572) -- connection lifecycle issues
- [Hackathon Time Management Guide](https://blog.hackunited.org/how-to-manage-time-effectively-in-hackathons) -- time-boxing strategies
- [Top 5 Hackathon Mistakes](https://medium.com/@BizthonOfficial/top-5-mistakes-developers-make-at-hackathons-and-how-to-avoid-them-d7e870746da1) -- scope creep patterns
- [TinyFish Cookbook](https://github.com/tinyfish-io/tinyfish-cookbook) -- sample apps and integration patterns

---
*Pitfalls research for: FraudFish autonomous fraud intelligence agent*
*Researched: 2026-03-24*
