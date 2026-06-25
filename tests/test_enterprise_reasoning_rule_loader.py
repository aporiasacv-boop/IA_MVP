import json
from pathlib import Path

from app.enterprise_reasoning.rule_loader import clear_rules_cache, load_enabled_rules, load_rule_packs


def test_load_rule_packs() -> None:
    clear_rules_cache()
    packs = load_rule_packs()
    assert len(packs) >= 3
    rules = load_enabled_rules()
    assert len(rules) >= 10
    assert all(rule.rule_code for rule in rules)


def test_rule_files_valid_json() -> None:
    rules_dir = Path(__file__).resolve().parents[1] / "app" / "enterprise_reasoning" / "rules"
    for path in rules_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "pack_id" in data
        assert "rules" in data
