"""Classification package for FraudFish verdict engine.

Two-tier classification: deterministic rules engine for obvious cases,
LLM fallback for ambiguous cases, validation layer for all paths.
Orchestrator function added in Plan 02.
"""
