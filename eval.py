import json
from app import ask

def main():
    with open("eval.json", encoding="utf-8") as f:
        cases = json.load(f)
    rows = []
    passed = 0
    for i, case in enumerate(cases, 1):
        result = ask(case["question"], case["as_of_date"])
        status_ok = result["status"] == case["expected_status"]
        answer_ok = case["expected_contains"].lower() in result["answer"].lower()
        citations_ok = all(any(expected in citation for citation in result["citations"])
                           for expected in case["expected_citations"])
        ok = status_ok and answer_ok and citations_ok
        passed += int(ok)
        rows.append((i, "PASS" if ok else "FAIL", status_ok, answer_ok, citations_ok,
                     case["question"]))
    print(f"{'ID':<4} {'RESULT':<7} {'STATUS':<7} {'ANSWER':<7} {'CITATIONS':<9} QUESTION")
    print("-" * 115)
    for row in rows:
        print(f"{row[0]:<4} {row[1]:<7} {str(row[2]):<7} {str(row[3]):<7} {str(row[4]):<9} {row[5]}")
    print(f"\nScore: {passed}/{len(cases)} ({passed/len(cases)*100:.1f}%)")
    print("Note: this is a lightweight smoke test, not a semantic evaluation.")
if __name__ == "__main__":
    main()
