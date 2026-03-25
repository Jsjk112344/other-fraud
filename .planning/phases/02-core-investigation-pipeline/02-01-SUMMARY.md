---
phase: 02-core-investigation-pipeline
plan: 01
subsystem: agents
tags: [tinyfish, asyncio, carousell, telegram, web-scraping, fallback]

# Dependency graph
requires:
  - phase: 01-application-skeleton-with-mocks
    provides: mock data infrastructure and step definitions
provides:
  - TinyFish async wrapper with timeout and thread isolation
  - Platform detection routing (Carousell, Telegram)
  - Carousell listing extractor with stealth mode and fallback
  - Telegram message extractor with fallback
affects: [02-core-investigation-pipeline, 03-classification-verdict-engine, 04-cross-platform-intelligence]

# Tech tracking
tech-stack:
  added: [tinyfish, python-dotenv]
  patterns: [asyncio.to_thread for sync-to-async, asyncio.wait_for timeout, silent mock fallback]

key-files:
  created:
    - backend/agents/carousell.py
    - backend/agents/telegram.py
  modified:
    - backend/agents/base.py
    - backend/agents/__init__.py
    - backend/agents/platform_detect.py
    - backend/tests/test_agents.py
    - backend/tests/test_platform_detect.py
    - backend/requirements.txt

key-decisions:
  - "Carousell uses stealth browser profile + SG proxy for Cloudflare bypass"
  - "Telegram uses default (non-stealth) profile since t.me is not bot-protected"
  - "Both extractors return (data, is_live) tuple for UI live badge support"

patterns-established:
  - "Extractor pattern: async function returns (dict, bool) where bool indicates live vs fallback data"
  - "TinyFish wrapper: _sync_extract in thread with asyncio.wait_for timeout"
  - "Normalizer pattern: raw TinyFish response mapped to standard schema dict"

requirements-completed: [PIPE-02]

# Metrics
duration: 5min
completed: 2026-03-25
---

# Phase 2 Plan 1: Listing Extractors Summary

**TinyFish async agent wrapper with Carousell (stealth+proxy) and Telegram extractors, platform URL routing, and silent mock fallback on failure**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-25T06:10:07Z
- **Completed:** 2026-03-25T06:15:05Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- TinyFish base wrapper with asyncio.to_thread + 15s wait_for timeout pattern
- Platform detection correctly routes Carousell and Telegram URLs, rejects unknowns
- Carousell extractor with stealth mode, SG proxy, and silent fallback to mock data
- Telegram message extractor with normalize and silent fallback
- 17 passing tests covering all extraction, fallback, and configuration scenarios

## Task Commits

Each task was committed atomically:

1. **Task 1: TinyFish base agent wrapper, platform detection, and test scaffolds** - `34ca922` (feat, pre-existing from 02-02 dependency)
2. **Task 2: Carousell and Telegram listing extractors with fallback** - `3f76363` (feat)

_Note: Task 1 artifacts (base.py, platform_detect.py, tests) were already committed as part of 02-02 execution which depended on this foundation. Task 2 added the new extractor modules._

## Files Created/Modified
- `backend/agents/base.py` - TinyFish async wrapper with _sync_extract, get_client, timeout
- `backend/agents/platform_detect.py` - URL domain routing to marketplace extractors
- `backend/agents/__init__.py` - Package exports for tinyfish_extract and detect_platform
- `backend/agents/carousell.py` - Carousell listing extraction with stealth, proxy, normalize, fallback
- `backend/agents/telegram.py` - Telegram message extraction with normalize, fallback
- `backend/tests/test_platform_detect.py` - 8 tests for URL platform detection
- `backend/tests/test_agents.py` - 9 tests for base wrapper, Carousell, and Telegram extractors
- `backend/requirements.txt` - Added tinyfish and python-dotenv dependencies

## Decisions Made
- Carousell uses stealth browser profile + SG proxy for Cloudflare bypass; Telegram uses default profile
- Both extractors return (data, is_live) tuple to support UI live badge indicator
- Price normalization handles string-to-float conversion with fallback to 0.0

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Python 3.9 compatibility for type hints**
- **Found during:** Task 1
- **Issue:** `str | None` syntax not supported at runtime in Python 3.9
- **Fix:** Linter auto-added `from __future__ import annotations` to all agent modules
- **Files modified:** backend/agents/base.py, backend/agents/platform_detect.py
- **Verification:** All tests pass on Python 3.9.6
- **Committed in:** 34ca922

**2. [Rule 3 - Blocking] Task 1 foundation already committed by 02-02 plan**
- **Found during:** Task 1
- **Issue:** base.py, platform_detect.py, and test files were already tracked in git from prior 02-02 execution
- **Fix:** Verified all acceptance criteria met, no new commit needed for Task 1
- **Files modified:** None (already committed)
- **Verification:** All 11 Task 1 tests pass, git diff shows no changes

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both issues resolved without scope change. Foundation was pre-built by dependent plan.

## Issues Encountered
- Task 1 files (base.py, platform_detect.py, tests) were already committed by the 02-02 plan execution which ran out of order. Verified correctness and proceeded to Task 2.

## User Setup Required

None - no external service configuration required. Tests run without TINYFISH_API_KEY.

## Next Phase Readiness
- Agent foundation complete for seller investigation (02-02) and event verification
- Carousell and Telegram extractors ready for integration into investigation pipeline
- Platform detection routes URLs to correct extractor automatically

---
*Phase: 02-core-investigation-pipeline*
*Completed: 2026-03-25*
