# Offline Policy Assistant

A small, deterministic, rule-based question-answering assistant for the three supplied merchant policy documents. No API key or third-party package is required.

## Run
1. Install Python 3.10+.
2. Open this folder in VS Code.
3. Run the interactive assistant:
   `python app.py`
4. Run the evaluation suite:
   `python eval.py`
5. Run the evaluation: `python eval.py`

## What works
- Offline, deterministic rules for UPI settlement, MDR/GST arithmetic, refunds, limits, account closure, card settlement, refund windows, and chargebacks.
- Date-sensitive refund answer before/after 1 September 2026.
- Responses contain status, answer, and source/clause citations.
- `eval.json` contains 16 tests, including adversarial stale-FAQ, false-premise, missing-information, and unsupported-topic questions.

## What doesn't
- This is a compact assignment solution, not general semantic retrieval.
- It recognizes common phrasings and may return CANNOT_ANSWER for paraphrases it does not recognize.
- The evaluation checks substrings and citation presence, not nuanced semantic correctness.
- The question router is keyword-based; add rules and tests before claiming broader coverage.

## Policy interpretation
The circular issued 20 July 2026 is effective 1 August 2026 unless a clause states otherwise. Its deletion of clause 3.3 takes effect 1 September 2026. The FAQ is treated as stale where it conflicts with the governing policy and amendment.
