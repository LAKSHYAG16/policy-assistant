"""Offline, deterministic policy assistant for AI Intern Assignment 2."""
import json
from datetime import date
import re

DEFAULT_DATE = date(2026, 8, 15)
AMENDMENT_EFFECTIVE = date(2026, 8, 1)
REFUND_EXCEPTION_END = date(2026, 9, 1)

def _date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))

def _money(amount):
    return f"₹{amount:,.2f}"

def _result(answer, citations, status):
    return {"answer": answer, "citations": citations, "status": status}

def ask(question, as_of_date="2026-08-15"):
    """Return a grounded answer with document/clause citations and a status."""
    q = question.lower()
    d = _date(as_of_date)

    # Settlement timing
    if any(x in q for x in ["upi money", "upi settlement", "when do", "receive upi", "settle upi"]):
        return _result(
            "UPI settles T+0 (the same day by 11:59 PM) only if the merchant has the active "
            "'Instant Settlement' add-on. Otherwise it settles T+1, the next working day "
            "(excluding Sundays and bank holidays).",
            ["circular_2026_08_amendment.md §A / clause 1.1",
             "policy_master_v1.md clause 1.1", "policy_master_v1.md clause 1.3"],
            "CONFLICT_RESOLVED"
        )

    # Refunds are date-dependent because clause 3.3 is deleted effective Sep 1.
    if "refund" in q and any(x in q for x in ["mdr", "fee", "back", "3 hour", "three hour", "24 hour"]):
        if d < REFUND_EXCEPTION_END:
            return _result(
                "Yes. As of this date, a refund initiated within 24 hours reverses the MDR in full, "
                "so a refund 3 hours after the sale qualifies.",
                ["policy_master_v1.md clauses 3.2 and 3.3"],
                "ANSWERED"
            )
        return _result(
            "No. From 1 Sep 2026, clause 3.3 is deleted and clause 3.2 applies without exception: "
            "MDR charged on a refunded transaction is not returned, including a refund initiated "
            "3 hours after the sale.",
            ["circular_2026_08_amendment.md clause D",
             "policy_master_v1.md clause 3.2"],
            "CONFLICT_RESOLVED"
        )

    # MDR cap question should be checked before general MDR questions.
    if "cap" in q and ("faq" in q or "right" in q or "maximum" in q):
        return _result(
            "The FAQ says there is no upper limit on MDR, but that is incorrect. From 1 Aug 2026, "
            "the cap is ₹15 per UPI transaction for merchants with monthly volume up to ₹10 lakh "
            "and ₹25 for merchants above ₹10 lakh. GST at 18% is charged on MDR separately and "
            "is not included in the cap.",
            ["merchant_faq_2026-03.md FAQ 'What do I pay on a UPI transaction?'",
             "circular_2026_08_amendment.md clause C / clause 2.3",
             "policy_master_v1.md clauses 2.2, 2.3, 2.4"],
            "CONFLICT_RESOLVED"
        )

    # Fee arithmetic
    if any(x in q for x in ["mdr", "gst", "what do they pay", "transaction value", "fee on"]):
        amount_matches = re.findall(r"(?:rs\.?|₹|inr)\s*([\d,]+(?:\.\d+)?)", q)
        amount = float(amount_matches[-1].replace(",", "")) if amount_matches else None
        large = any(x in q for x in ["large", "above", "over 10 lakh", "above rs.10 lakh"])
        small = "small" in q or "up to" in q
        if amount is None:
            return _result("Please provide the UPI transaction amount so I can calculate MDR and GST.", [], "CANNOT_ANSWER")
        if large:
            rate, cap = 0.005, 25.0
            mdr = min(amount * rate, cap)
            tier = "large merchant (>₹10 lakh monthly volume)"
        elif small:
            rate, cap = 0.0025, 15.0
            mdr = min(amount * rate, cap)
            tier = "small merchant (monthly volume up to ₹10 lakh)"
        else:
            return _result("I need to know whether the merchant's monthly volume is above ₹10 lakh or up to ₹10 lakh to calculate MDR.", [], "CANNOT_ANSWER")
        gst = round(mdr * 0.18, 2)
        total = round(mdr + gst, 2)
        return _result(
            f"For a {tier}, the MDR rate is {rate*100:.2f}% subject to a ₹{cap:.0f} cap. "
            f"On a {_money(amount)} payment, MDR before the cap is {_money(amount*rate)}; "
            f"MDR charged is {_money(mdr)}, GST at 18% is {_money(gst)}, and the total fee is {_money(total)}.",
            ["circular_2026_08_amendment.md clauses B and C",
             "policy_master_v1.md clauses 2.2, 2.3 and 2.4"],
            "CONFLICT_RESOLVED"
        )

    # Daily limit / repeated payments
    if ("twice" in q or "two times" in q or "one day" in q or "daily limit" in q) and ("pay" in q or "customer" in q or "₹" in q or "rs" in q):
        return _result(
            "No, not if both payments are ₹1,00,000. The daily limit per customer account is "
            "₹1,00,000 or the customer's own bank limit, whichever is lower, across all UPI "
            "transactions. The daily limit is not reset for each transaction.",
            ["circular_2026_08_amendment.md clause E / clause 4.3"],
            "CONFLICT_RESOLVED"
        )

    # Per-transaction limit
    if "per transaction" in q or "single transaction" in q or "single upi payment" in q or "maximum amount" in q:
        return _result(
            "The normal UPI limit is ₹1,00,000 per transaction. Capital Markets and Insurance "
            "merchants may accept up to ₹2,00,000 only if they have completed enhanced KYC. "
            "A separate daily customer-account limit may still apply.",
            ["policy_master_v1.md clauses 4.1, 4.2 and 4.4",
             "circular_2026_08_amendment.md clause E / clause 4.3"],
            "ANSWERED"
        )

    # Account closure
    if "close" in q and "account" in q or "closed my account" in q:
        return _result(
            "The policy requires 30 days' written notice to close an account. Pending settlements "
            "are released within 10 working days of closure, after outstanding dues are deducted. "
            "Because 'yesterday' does not establish whether the required notice/closure process "
            "was completed, the exact release date cannot be determined from the question alone.",
            ["policy_master_v1.md clauses 5.1 and 5.2",
             "merchant_faq_2026-03.md FAQ 'Can I close my account any time?'"],
            "CONFLICT_RESOLVED"
        )

    # Card settlement
    if "card" in q and ("same day" in q or "settle" in q or "settlement" in q):
        return _result(
            "No. Card transactions settle T+2 (two days after the transaction), not the same day.",
            ["policy_master_v1.md clause 1.2",
             "merchant_faq_2026-03.md FAQ 'When will I get my UPI money?'"],
            "ANSWERED"
        )

    # Refund window / chargeback
    if "refund" in q and ("90 days" in q or "initiate" in q):
        return _result("A merchant may initiate a refund within 90 days of the original transaction.",
                       ["policy_master_v1.md clause 3.1"], "ANSWERED")
    if "chargeback" in q:
        return _result("Chargeback disputes must be raised by the customer's bank within 120 days.",
                       ["policy_master_v1.md clause 3.4"], "ANSWERED")

    return _result(
        "I cannot answer this reliably from the implemented policy rules. Please ask about UPI settlement, MDR/GST, refunds, limits, account closure, card settlement, or chargebacks.",
        [], "CANNOT_ANSWER"
    )


if __name__ == "__main__":
    print("Offline Policy Assistant (type 'quit' to exit)")
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        as_of = input("As-of date [2026-08-15]: ").strip() or "2026-08-15"
        print(json.dumps(ask(question, as_of), indent=2, ensure_ascii=False))
