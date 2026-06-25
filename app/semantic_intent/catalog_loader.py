import json
import unicodedata
from functools import lru_cache
from pathlib import Path

from app.semantic_intent.schemas import (
    BusinessContextDefinition,
    BusinessObjectDefinition,
    BusinessVerbDefinition,
)

CATALOG_DIR = Path(__file__).resolve().parent / "catalog"


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    normalized = unicodedata.normalize("NFD", lowered)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


@lru_cache(maxsize=1)
def load_verbs() -> list[BusinessVerbDefinition]:
    raw = json.loads((CATALOG_DIR / "verbs.json").read_text(encoding="utf-8"))
    return [BusinessVerbDefinition(**item) for item in raw["verbs"]]


@lru_cache(maxsize=1)
def load_objects() -> list[BusinessObjectDefinition]:
    raw = json.loads((CATALOG_DIR / "objects.json").read_text(encoding="utf-8"))
    return [BusinessObjectDefinition(**item) for item in raw["objects"]]


@lru_cache(maxsize=1)
def load_contexts() -> list[BusinessContextDefinition]:
    raw = json.loads((CATALOG_DIR / "objects.json").read_text(encoding="utf-8"))
    return [BusinessContextDefinition(**item) for item in raw.get("contexts", [])]


def load_enabled_verbs() -> list[BusinessVerbDefinition]:
    return [verb for verb in load_verbs() if verb.enabled]


def build_verb_patterns() -> list[tuple[str, BusinessVerbDefinition, str]]:
    patterns: list[tuple[str, BusinessVerbDefinition, str]] = []
    for verb in load_verbs():
        if not verb.enabled:
            continue
        patterns.append((normalize_text(verb.verb_id.replace("_", " ")), verb, verb.verb_id))
        for alias in verb.aliases:
            patterns.append((normalize_text(alias), verb, alias))
    patterns.sort(key=lambda item: len(item[0]), reverse=True)
    return patterns


def clear_catalog_cache() -> None:
    load_verbs.cache_clear()
    load_objects.cache_clear()
    load_contexts.cache_clear()
