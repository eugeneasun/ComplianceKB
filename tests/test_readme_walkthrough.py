"""Verify that the teaching example matches the frozen source, scenario and answer."""
from pathlib import Path
import csv,json

ROOT=Path(__file__).resolve().parents[1]
example=json.loads((ROOT/'examples/end_to_end_loto.json').read_text(encoding='utf-8'))
records=json.loads((ROOT/'data/releases/v1.2.0/all_requirements.json').read_text(encoding='utf-8'))['requirements']
record=next(r for r in records if r['id']=='OSHA-LOTO-005')
assert example['record']==record
with (ROOT/'research/benchmark/scenarios_HUMAN_CONFIRMED_DEVELOPMENT.csv').open(encoding='utf-8-sig',newline='') as f:
    scenario=next(s for s in csv.DictReader(f) if s['scenario_id']=='DEV-006')
assert example['scenario']==scenario
saved=json.loads((ROOT/example['saved_call_path']).read_text(encoding='utf-8'))
assert example['saved_answer']==saved['answer']
assert example['saved_call_prompt_sha256']==saved['prompt_sha256']
assert example['human_review']['performed_on_actual_workplace'] is False
assert set(saved['answer']['predicted_requirement_ids'])==set(scenario['gold_requirement_ids'].split('|'))
for label,gold in [('predicted_trigger_labels','gold_trigger_labels'),('predicted_evidence_labels','gold_evidence_labels'),('predicted_citations','gold_citations')]:
    assert set(saved['answer'][label])==set(scenario[gold].split('|'))
failure=json.loads((ROOT/'research/benchmark/runs/llm_development_20260927/openai/rkm_agent/DEV-002.json').read_text(encoding='utf-8'))['answer']
assert set(failure['predicted_requirement_ids'])=={'OSHA-HAZCOM-007','OSHA-HAZCOM-016'}
print('PASS: homepage example matches frozen source/scenario/answer; human verification remains explicitly unperformed; contrasting failure preserved')
