import json
from functools import lru_cache

from app.enterprise_reasoning.constants import RULES_DIR
from app.enterprise_reasoning.schemas import ReasoningRuleDefinition, ReasoningRulePack


def _load_pack_file(path) -> ReasoningRulePack:
    raw = json.loads(path.read_text(encoding="utf-8"))
    pack_id = raw["pack_id"]
    rules = []
    for item in raw.get("rules", []):
        rules.append(
            ReasoningRuleDefinition(
                pack_id=pack_id,
                **item,
            )
        )
    return ReasoningRulePack(pack_id=pack_id, version=raw.get("version", "1.0.0"), rules=rules)


@lru_cache(maxsize=1)
def load_rule_packs() -> list[ReasoningRulePack]:
    if not RULES_DIR.is_dir():
        return []
    packs: list[ReasoningRulePack] = []
    for path in sorted(RULES_DIR.glob("*.json")):
        packs.append(_load_pack_file(path))
    return packs


def load_enabled_rules() -> list[ReasoningRuleDefinition]:
    rules: list[ReasoningRuleDefinition] = []
    for pack in load_rule_packs():
        rules.extend(rule for rule in pack.rules if rule.enabled)
    return rules


def clear_rules_cache() -> None:
    load_rule_packs.cache_clear()
