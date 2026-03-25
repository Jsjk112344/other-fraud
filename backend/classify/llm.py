"""OpenAI gpt-4o structured output classification for ambiguous fraud cases."""

import json
from openai import AsyncOpenAI
from models.events import VerdictResult

_client = None


def _get_client() -> AsyncOpenAI:
    """Lazy-initialize the OpenAI client (avoids import-time API key requirement)."""
    global _client
    if _client is None:
        _client = AsyncOpenAI()  # Reads OPENAI_API_KEY from environment
    return _client

SYSTEM_PROMPT = """You are a fraud classification expert for Singapore ticket marketplaces.

Analyze the investigation evidence and classify this listing into one of four categories:
- LEGITIMATE: Real ticket, fair price, trustworthy seller
- SCALPING_VIOLATION: Real ticket but significantly marked up beyond face value
- LIKELY_SCAM: Strong indicators of fraud (extreme underpricing, fake seller, suspicious patterns)
- COUNTERFEIT_RISK: Indicators of counterfeit tickets (wrong venue details, suspicious transfer methods)

Evaluate all 5 risk signals:
1. Pricing Anomaly - How does the price compare to face value and market average?
2. Seller Reputation - Account age, review history, listing patterns
3. Event Verification - Does the event exist? Is the ticket category real?
4. Cross-Platform Duplicates - Same listing found elsewhere under different names?
5. Listing Authenticity - Payment method, description quality, transfer method red flags

For each signal, assign:
- severity: CRITICAL, WARNING, NEUTRAL, or CLEAR
- segmentsFilled: 1-5 (1=minimal concern, 5=maximum concern)

Provide a confidence score (0-100) and 2-3 sentence reasoning summary hitting key evidence points.
Focus on Singapore context: Carousell norms, SGD pricing, local events."""


def format_evidence(evidence: dict) -> str:
    """Format investigation evidence as structured text for the LLM."""
    return f"Investigation evidence for classification:\n\n{json.dumps(evidence, indent=2, default=str)}"


async def classify_with_llm(evidence: dict) -> VerdictResult:
    """Classify a listing using OpenAI gpt-4o structured output.

    Sends full evidence dump (no pre-filtering per user decision).
    Returns VerdictResult deserialized directly from gpt-4o response.
    """
    client = _get_client()
    completion = await client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": format_evidence(evidence)},
        ],
        response_format=VerdictResult,
        max_tokens=2000,
        temperature=0.3,
    )
    result = completion.choices[0].message.parsed
    if result is None:
        raise ValueError("OpenAI model refused to classify -- no parsed result")
    return result
