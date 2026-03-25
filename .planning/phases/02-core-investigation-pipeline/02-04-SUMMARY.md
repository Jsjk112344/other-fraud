---
phase: 02-core-investigation-pipeline
plan: 04
subsystem: agents
tags: [asyncio, pipeline, parallel, sse, tdd]

requires:
  - phase: 02-core-investigation-pipeline/02-01
    provides: Carousell and Telegram listing extractors
  - phase: 02-core-investigation-pipeline/02-02
    provides: Seller investigation agents (Carousell + Telegram)
  - phase: 02-core-investigation-pipeline/02-03
    provides: Official price verification agent with three-tier fallback
provides:
  - Live investigation pipeline orchestrator with parallel fan-out via asyncio.gather
  - SSE endpoint wired to live pipeline (replacing mock)
  - LIVE badge on frontend StepCard for live data
affects: [03-classification-engine, 04-cross-platform-intelligence, frontend]

tech-stack:
  added: []
  patterns: [async-generator-pipeline, parallel-fan-out-with-gather, live-flag-propagation]

key-files:
  created:
    - backend/agents/pipeline.py
    - backend/tests/test_pipeline.py
  modified:
    - backend/api/investigate.py
    - frontend/src/components/StepCard.tsx
    - backend/tests/test_api.py

key-decisions:
  - "Live pipeline replaces mock via try/except import with mock as fallback"
  - "LIVE badge only shown for _live=true; no CACHED indicator for fallback data"

patterns-established:
  - "Pipeline pattern: sequential extraction then parallel fan-out via asyncio.gather"
  - "Live flag propagation: agents return (data, is_live) tuple, pipeline adds _live to event data dict"

requirements-completed: [PIPE-07]

duration: 4min
completed: 2026-03-25
---

# Phase 2 Plan 4: Live Investigation Pipeline Summary

**Parallel asyncio.gather pipeline wiring all agents with 60s timeout, SSE integration, and frontend LIVE badge**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-25T06:18:21Z
- **Completed:** 2026-03-25T06:22:34Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Live investigation pipeline orchestrates listing extraction sequentially then fans out seller + event verification in parallel
- SSE endpoint now uses live pipeline with automatic mock fallback
- Frontend StepCard shows green LIVE badge with accessible aria-label on steps with live data
- 8 new pipeline tests plus all 84 backend tests passing

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Failing pipeline tests** - `58acdcb` (test)
2. **Task 1 GREEN: Pipeline implementation** - `8c75bb4` (feat)
3. **Task 2: SSE wiring + LIVE badge** - `97bd2fe` (feat)

_Note: Task 1 used TDD with RED/GREEN commits_

## Files Created/Modified
- `backend/agents/pipeline.py` - Live investigation orchestrator with parallel fan-out and 60s timeout
- `backend/tests/test_pipeline.py` - 8 tests covering parallel execution, timeout, live badge, platform routing, event order
- `backend/api/investigate.py` - SSE endpoint now uses live pipeline with mock fallback
- `frontend/src/components/StepCard.tsx` - Green LIVE badge for steps with live data
- `backend/tests/test_api.py` - Updated SSE event count test for live pipeline

## Decisions Made
- Live pipeline replaces mock via try/except import with mock as fallback if agents module unavailable
- LIVE badge only shown when _live=true; no indicator for fallback data (clean UI)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated test_api.py SSE event count assertion**
- **Found during:** Task 2 (SSE wiring)
- **Issue:** test_sse_stream_contains_all_events expected 13 events (mock pipeline) but live pipeline produces 6
- **Fix:** Updated test to expect 6+ events and check for _live field in COMPLETE events
- **Files modified:** backend/tests/test_api.py
- **Verification:** All 84 tests pass
- **Committed in:** 97bd2fe (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Test update necessary to match new pipeline behavior. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Full investigation pipeline is operational with live TinyFish extraction and automatic fallback
- Classification engine (Phase 3) can consume pipeline events for verdict generation
- Cross-platform intelligence (Phase 4) can extend the pipeline with additional investigation steps

---
*Phase: 02-core-investigation-pipeline*
*Completed: 2026-03-25*
