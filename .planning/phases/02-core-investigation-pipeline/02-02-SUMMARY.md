---
phase: 02-core-investigation-pipeline
plan: 02
subsystem: agents
tags: [tinyfish, carousell, telegram, seller-investigation, sentiment-analysis, web-scraping]

# Dependency graph
requires:
  - phase: 01-application-skeleton-with-mocks
    provides: mock data layer and SSE streaming pipeline
provides:
  - Carousell seller profile extraction with full review parsing and sentiment analysis
  - Telegram repeat-seller detection via group message scanning
  - Shared TinyFish async extraction base module
affects: [03-classification-and-verdict-engine, 04-cross-platform-intelligence]

# Tech tracking
tech-stack:
  added: []
  patterns: [async-tinyfish-extract-with-fallback, tdd-red-green-commit, keyword-sentiment-analysis]

key-files:
  created:
    - backend/agents/base.py
    - backend/agents/seller.py
    - backend/agents/seller_telegram.py
    - backend/tests/test_seller.py
  modified:
    - backend/mock/data.py

key-decisions:
  - "Added get_mock_data helper to mock/data.py for step-based fallback lookup"
  - "Telegram fallback returns single-poster assumption rather than cached mock data"
  - "Review sentiment uses keyword-based classification (positive/negative/neutral) not ML"

patterns-established:
  - "Agent fallback pattern: try tinyfish_extract, return (data, True) on success, (fallback, False) on None"
  - "TinyFish wrapper pattern: async with timeout via asyncio.wait_for + to_thread"
  - "Seller module naming: seller.py for Carousell, seller_telegram.py for Telegram"

requirements-completed: [PIPE-03]

# Metrics
duration: 4min
completed: 2026-03-25
---

# Phase 2 Plan 2: Seller Investigation Agents Summary

**Carousell seller profile extraction with full review parsing and sentiment analysis, plus Telegram repeat-seller detection via group message scanning -- both with silent TinyFish fallback**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-25T06:09:55Z
- **Completed:** 2026-03-25T06:13:28Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Carousell seller investigation extracts account age, total listings, categories, all reviews, and keyword-based sentiment summary
- Telegram repeat-seller detection scans group for multiple messages from same user, determines repeat_seller boolean
- Both agents silently fall back to cached/default data when TinyFish calls fail or time out
- 15 tests all pass without TINYFISH_API_KEY set

## Task Commits

Each task was committed atomically:

1. **Task 1: Carousell seller profile investigation agent with full review parsing** - `34ca922` (feat)
2. **Task 2: Telegram repeat-seller detection agent** - `3f544a1` (feat)

_Note: TDD tasks -- tests written first (RED), then implementation (GREEN), committed together per task._

## Files Created/Modified
- `backend/agents/base.py` - Async TinyFish extraction wrapper with timeout and thread isolation
- `backend/agents/seller.py` - Carousell seller profile extraction, URL builder, review sentiment analysis, normalization
- `backend/agents/seller_telegram.py` - Telegram repeat-seller detection, group URL parsing, normalization
- `backend/agents/__init__.py` - Package init with base imports
- `backend/tests/test_seller.py` - 15 tests covering both Carousell and Telegram seller agents
- `backend/mock/data.py` - Added get_mock_data helper for step-based fallback

## Decisions Made
- Added `get_mock_data()` helper to mock/data.py since plan referenced it but it didn't exist
- Telegram fallback uses inline dict (single-poster assumption) rather than mock data lookup since Telegram has no pre-scraped mock
- Review sentiment is keyword-based (fast, deterministic) -- ML-based sentiment deferred to classification engine

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created agents/base.py and agents directory**
- **Found during:** Task 1 (pre-implementation)
- **Issue:** `backend/agents/` directory and `base.py` module did not exist; plan imports depend on them
- **Fix:** Created agents directory, __init__.py, and base.py with async TinyFish wrapper
- **Files modified:** backend/agents/__init__.py, backend/agents/base.py
- **Verification:** All imports resolve, tests pass
- **Committed in:** 34ca922

**2. [Rule 3 - Blocking] Added get_mock_data to mock/data.py**
- **Found during:** Task 1 (pre-implementation)
- **Issue:** Plan references `from mock.data import get_mock_data` but function didn't exist
- **Fix:** Added `get_mock_data(step_id)` helper that looks up MOCK_STEPS dict
- **Files modified:** backend/mock/data.py
- **Verification:** Fallback test passes
- **Committed in:** 34ca922

**3. [Rule 1 - Bug] Fixed Python 3.9 type annotation compatibility**
- **Found during:** Task 1 (test execution)
- **Issue:** `str | None` union syntax fails on Python 3.9 (system Python)
- **Fix:** Linter auto-added `from __future__ import annotations` to affected files
- **Files modified:** backend/agents/base.py, backend/agents/platform_detect.py
- **Verification:** All tests pass on Python 3.9
- **Committed in:** 34ca922

---

**Total deviations:** 3 auto-fixed (1 bug, 2 blocking)
**Impact on plan:** All auto-fixes necessary for correctness and functionality. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Seller investigation agents ready for integration into live investigation pipeline
- base.py provides shared tinyfish_extract for all future agents (event verification, market check, etc.)
- Fallback pattern established for all future agents to follow

---
*Phase: 02-core-investigation-pipeline*
*Completed: 2026-03-25*
