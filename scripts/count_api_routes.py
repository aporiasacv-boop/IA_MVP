"""Cuenta decoradores de rutas FastAPI en el proyecto."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "app"
PATTERN = re.compile(
    r'@(?:router|cost_router)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)'
)

def main() -> None:
    total = 0
    by_file: dict[str, int] = {}
    for path in sorted(ROOT.rglob("*.py")):
        if "routes" not in path.parts and path.name != "routes.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = list(PATTERN.finditer(text))
        if matches:
            by_file[str(path.relative_to(ROOT.parent))] = len(matches)
            total += len(matches)
    print(f"TOTAL_ENDPOINTS={total}")
    for file_path, count in by_file.items():
        print(f"{count}\t{file_path}")

if __name__ == "__main__":
    main()
