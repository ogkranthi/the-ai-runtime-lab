"""Reference triage agent for AI Runtime Field Challenge 01.

One combined LLM call per complaint. The model chooses a routing team, sets the
risk flag, and selects verbatim evidence quotes. Deterministic code handles the
orchestration, schema validation, and the fallback.

Provider-agnostic: --provider anthropic|openai (default anthropic). The model
strings live in MODEL_DEFAULTS so they are easy to update.

Usage:
    python agent/run_agent.py --input data/complaints.jsonl \
        --output outputs/predictions.jsonl --limit 10
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Default model per provider. Verify and update these to the current model
# strings for your account before a full run.
MODEL_DEFAULTS = {
    "anthropic": "claude-sonnet-5",
    "openai": "gpt-4.1",
}

ROUTING_TEAMS = [
    "account_access", "payments_transfers", "fraud_disputes",
    "credit_lending", "customer_service", "other",
]
STEPS = ["signal_extraction", "routing_classification", "risk_flagging", "evidence_selection"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def load_prompt_parts():
    return {
        "system": _read(os.path.join(HERE, "prompts", "system.md")),
        "triage": _read(os.path.join(HERE, "prompts", "triage.md")),
        "brief": _read(os.path.join(ROOT, "brief.md")),
        "rubric": _read(os.path.join(ROOT, "rubric.md")),
    }


def load_schema():
    return json.loads(_read(os.path.join(HERE, "schemas", "prediction.schema.json")))


def validate(record: dict, schema: dict):
    """Validate with jsonschema when available, else a manual structural check.

    Returns None on success or a short error string on failure.
    """
    try:
        import jsonschema
        try:
            jsonschema.validate(record, schema)
            return None
        except jsonschema.ValidationError as exc:
            return exc.message
    except ImportError:
        return _manual_validate(record)


def _manual_validate(record: dict):
    required = ["complaint_id", "routing_team", "risk_flag", "confidence", "ai_usage", "reason", "evidence"]
    for key in required:
        if key not in record:
            return f"missing field: {key}"
    if record["routing_team"] not in ROUTING_TEAMS:
        return f"routing_team not in enum: {record['routing_team']}"
    if not isinstance(record["risk_flag"], bool):
        return "risk_flag must be boolean"
    if not isinstance(record["confidence"], (int, float)):
        return "confidence must be a number"
    if not isinstance(record.get("reason"), str) or not record["reason"].strip():
        return "reason must be a non-empty string"
    ai = record.get("ai_usage")
    if not isinstance(ai, dict) or not all(k in ai for k in ("provider", "model", "steps")):
        return "ai_usage missing provider, model, or steps"
    ev = record.get("evidence")
    if not isinstance(ev, list) or not ev:
        return "evidence must be a non-empty list"
    for item in ev:
        if not all(k in item for k in ("criterion", "source_id", "quote")):
            return "evidence item missing criterion, source_id, or quote"
    return None


def build_user_prompt(parts: dict, complaint: dict) -> str:
    return (
        "CUSTOMER BRIEF\n" + parts["brief"] + "\n\n"
        "SCORING RUBRIC\n" + parts["rubric"] + "\n\n"
        "TRIAGE INSTRUCTIONS\n" + parts["triage"] + "\n\n"
        "COMPLAINT (decide only from this record)\n"
        + json.dumps(complaint, ensure_ascii=False)
    )


def call_anthropic(model: str, system: str, user: str):
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=1200,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = msg.content[0].text
    usage = getattr(msg, "usage", None)
    tokens = (getattr(usage, "input_tokens", 0), getattr(usage, "output_tokens", 0)) if usage else (0, 0)
    return text, tokens


def call_openai(model: str, system: str, user: str):
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    text = resp.choices[0].message.content
    usage = getattr(resp, "usage", None)
    tokens = (getattr(usage, "prompt_tokens", 0), getattr(usage, "completion_tokens", 0)) if usage else (0, 0)
    return text, tokens


def _strip_fences(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.endswith("```"):
            t = t[:-3]
        if t.lower().startswith("json"):
            t = t[4:]
    return t.strip()


def assemble(complaint: dict, core: dict, provider: str, model: str) -> dict:
    """Merge the model's core decision with the fields the harness owns."""
    return {
        "complaint_id": complaint["complaint_id"],
        "routing_team": core.get("routing_team"),
        "risk_flag": core.get("risk_flag"),
        "confidence": core.get("confidence"),
        "ai_usage": {"provider": provider, "model": model, "steps": STEPS},
        "reason": core.get("reason"),
        "evidence": core.get("evidence"),
    }


def fallback(complaint: dict, provider: str, model: str, note: str) -> dict:
    """Schema-valid record used when the model output cannot be parsed."""
    source = complaint["sources"][0]
    quote = " ".join(source["text"].split())[:60].strip()
    return {
        "complaint_id": complaint["complaint_id"],
        "routing_team": "other",
        "risk_flag": False,
        "confidence": 0.0,
        "ai_usage": {"provider": provider, "model": model, "steps": STEPS},
        "reason": f"Parse failure, defaulted to other and risk_flag false. {note}",
        "evidence": [{"criterion": "routing_team", "source_id": source["source_id"], "quote": quote}],
    }


def predict_one(complaint, parts, schema, caller, provider, model):
    system = parts["system"]
    user = build_user_prompt(parts, complaint)
    last_err = ""
    for attempt in range(2):
        text, tokens = caller(model, system, user)
        try:
            core = json.loads(_strip_fences(text))
            record = assemble(complaint, core, provider, model)
        except Exception as exc:  # noqa: BLE001 - any parse issue triggers retry
            last_err = f"json error: {exc}"
            continue
        err = validate(record, schema)
        if err is None:
            return record, tokens
        last_err = err
    return fallback(complaint, provider, model, last_err), tokens


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reference triage agent for Challenge 01.")
    ap.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    ap.add_argument("--model", default=None)
    ap.add_argument("--input", default="data/complaints.jsonl")
    ap.add_argument("--output", default="outputs/predictions.jsonl")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args(argv)

    key_env = "ANTHROPIC_API_KEY" if args.provider == "anthropic" else "OPENAI_API_KEY"
    if not os.environ.get(key_env):
        print(f"Missing {key_env}. Set it for provider '{args.provider}'.", file=sys.stderr)
        print("Example: export ANTHROPIC_API_KEY=your_key_here", file=sys.stderr)
        return 2

    model = args.model or MODEL_DEFAULTS[args.provider]
    caller = call_anthropic if args.provider == "anthropic" else call_openai
    parts = load_prompt_parts()
    schema = load_schema()

    complaints = []
    with open(args.input, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                complaints.append(json.loads(line))
    if args.limit is not None:
        complaints = complaints[: args.limit]

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    total_in = total_out = 0
    with open(args.output, "w", encoding="utf-8") as out:
        for i, complaint in enumerate(complaints, 1):
            record, (tin, tout) = predict_one(complaint, parts, schema, caller, args.provider, model)
            total_in += tin
            total_out += tout
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"[{i}/{len(complaints)}] {complaint['complaint_id']} "
                  f"-> {record['routing_team']}, risk={record['risk_flag']} "
                  f"(in={total_in} out={total_out} tokens)")

    print(f"Wrote {len(complaints)} predictions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
