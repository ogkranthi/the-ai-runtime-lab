# Agent

`run_agent.py` is the reference triage agent. It is simple and honest: one
combined LLM call per complaint. The model does the reasoning (routing, risk,
evidence). Deterministic code does the orchestration, schema validation, and the
fallback.

## Run it

```bash
export ANTHROPIC_API_KEY=your_key_here
python agent/run_agent.py --input data/complaints.jsonl \
    --output outputs/predictions.jsonl --limit 10
```

Options:

- `--provider anthropic|openai` (default anthropic). Reads `ANTHROPIC_API_KEY` or
  `OPENAI_API_KEY` and prints a helpful error if the key is missing.
- `--model` overrides the default. Defaults live in `MODEL_DEFAULTS` at the top of
  `run_agent.py`. Verify the model strings against your account before a full run.
- `--input`, `--output`, `--limit`. `--limit` defaults to all complaints.

## How it works

1. Compose the prompt from `brief.md`, `rubric.md`, and the files in `prompts/`.
2. Ask the model for a strict JSON object (routing team, risk flag, confidence,
   reason, evidence quotes). Temperature is 0.
3. Merge the model's decision with the fields the harness owns (`complaint_id`,
   `ai_usage`) and validate against `schemas/prediction.schema.json`.
4. On a validation failure, retry once. If it still fails, write a fallback
   record: `routing_team: other`, `risk_flag: false`, with a reason noting the
   parse failure. The fallback stays schema-valid.

No web access, no live data. The agent reads only the cached narratives.

## Prompts

- `prompts/system.md`: the standing rules (use only the narrative, do not invent,
  tone is not risk, short can still be severe, return only JSON).
- `prompts/triage.md`: the four-step task and the exact JSON shape to return.

Edit the prompts to change agent behavior. That is the main lever for a mini
report.
