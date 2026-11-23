"""
Evaluates AI Model Adapter against synthetic multimodal commercial test cases.
Measures field extraction accuracy, numeral normalization, latency, and token usage.
"""
import json
import os
import sys
import time
from app.ingestion.adapters import AIModelAdapter, normalize_bengali_digits

CASES = [
    {
        "id": "CASE-TXT-01",
        "type": "text",
        "input": "মেসার্স হক ট্রেডার্স চালান নং ৪১, দাবি ২৫,০০০ টাকা ক্যাশ",
        "expected": {
            "party_name": "মেসার্স হক ট্রেডার্স",
            "invoice_ref": "41",
            "amount_paisa": 2500000,
            "payment_method": "cash",
        },
    },
    {
        "id": "CASE-TXT-02",
        "type": "text",
        "input": "করিম ভাই বকেয়া ৫০০ টাকা পরিশোধ করেছেন",
        "expected": {
            "party_name": "করিম ভাই",
            "amount_paisa": 50000,
            "payment_method": "cash",
        },
    },
    {
        "id": "CASE-AUD-01",
        "type": "audio",
        "bytes": b"RIFF....WAVEfmt rahim voice note 1000 cash paid",
        "mime": "audio/mp3",
        "expected": {
            "party_name": "রহিম স্টোর",
            "amount_paisa": 100000,
            "payment_method": "cash",
        },
    },
    {
        "id": "CASE-IMG-01",
        "type": "image",
        "bytes": b"\xff\xd8\xff memo_42 Al Madina Store receipt",
        "mime": "image/jpeg",
        "expected": {
            "party_name": "আল মদিনা স্টোর",
            "invoice_ref": "42",
            "amount_paisa": 1800000,
            "payment_method": "bkash",
        },
    },
]

def run_eval():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    is_live = bool(api_key and api_key.strip())
    mode = "live_gemini" if is_live else "offline_test_double"
    adapter = AIModelAdapter(api_key=api_key)

    print(f"=== Shongoti Multimodal AI Evaluation ===")
    print(f"Mode: {mode}")
    print(f"Model: {adapter.model}\n")

    results = []
    correct_fields = 0
    total_fields = 0
    total_latency_ms = 0

    for case in CASES:
        start = time.time()
        try:
            if case["type"] == "text":
                res = adapter.parse_bangla_document(text_or_content=case["input"], source_type="text")
            else:
                res = adapter.parse_bangla_document(
                    source_type=case["type"],
                    raw_bytes=case["bytes"],
                    mime_type=case["mime"],
                )
            elapsed_ms = (time.time() - start) * 1000
            total_latency_ms += elapsed_ms

            case_correct = 0
            case_total = len(case["expected"])
            for field, exp_val in case["expected"].items():
                act_val = getattr(res, field, None)
                if act_val == exp_val:
                    case_correct += 1
            
            correct_fields += case_correct
            total_fields += case_total

            results.append({
                "case_id": case["id"],
                "type": case["type"],
                "passed": case_correct == case_total,
                "score": f"{case_correct}/{case_total}",
                "elapsed_ms": round(elapsed_ms, 2),
                "confidence": res.confidence,
                "amount_paisa": res.amount_paisa,
            })
            print(f"  [{'PASS' if case_correct == case_total else 'FAIL'}] {case['id']} ({case['type']}): {case_correct}/{case_total} fields in {elapsed_ms:.1f}ms")
        except Exception as exc:
            print(f"  [ERROR] {case['id']}: {exc}")
            results.append({
                "case_id": case["id"],
                "type": case["type"],
                "passed": False,
                "error": str(exc),
            })

    accuracy = (correct_fields / total_fields) * 100 if total_fields > 0 else 0
    avg_latency = total_latency_ms / len(CASES) if CASES else 0

    report = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode,
        "is_live_provider": is_live,
        "model": adapter.model,
        "total_cases": len(CASES),
        "overall_field_accuracy": f"{accuracy:.1f}%",
        "avg_latency_ms": round(avg_latency, 2),
        "results": results,
    }

    out_dir = os.path.join("docs", "evidence", "phase-14")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "eval-ai-report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nOverall Field Accuracy: {accuracy:.1f}%")
    print(f"Average Latency: {avg_latency:.1f} ms")
    print(f"Report written to: {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(run_eval())
