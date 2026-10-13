# Where it breaks

1. **Unrecognized paraphrases or multi-intent questions.** The router uses keyword rules rather than semantic search. A differently phrased question can fall through to CANNOT_ANSWER even if the source contains the answer.
2. **Complex settlement date calculation.** The assistant explains T+1 and the exclusion of Sundays/bank holidays but does not calculate an exact date because a holiday calendar and transaction timestamp are not supplied.
3. **Missing merchant-specific facts.** It cannot verify whether a merchant has the Instant Settlement add-on, completed enhanced KYC, or the customer's bank has a lower limit. It states the conditions rather than pretending to know those facts.
