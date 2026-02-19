import json
from pathlib import Path
from jsonschema import validate

BASE = Path(__file__).resolve().parents[1]

samples = {
    "extract.output.schema.json": {
        "candidates": [
            {"type": "preference", "key": "briefing_tone", "value": "친근하게", "confidence": 0.9}
        ]
    },
    "normalize.output.schema.json": {
        "normalized": [
            {"type": "preference", "canonical_key": "briefing_tone", "value": "친근하게", "confidence": 0.9}
        ]
    },
    "validate.output.schema.json": {
        "accepted": [
            {"type": "preference", "canonical_key": "briefing_tone", "value": "친근하게", "confidence": 0.9, "ttl_days": None}
        ],
        "rejected": []
    }
}

for name, sample in samples.items():
    schema = json.loads((BASE / 'schemas' / name).read_text(encoding='utf-8'))
    validate(instance=sample, schema=schema)

print('schema tests passed')
