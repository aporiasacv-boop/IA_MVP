import re
from pathlib import Path

from app.enterprise_knowledge_service.providers.base import KnowledgeProvider
from app.enterprise_knowledge_service.schemas import KnowledgeDocument

PACK_ROOT = Path(__file__).resolve().parents[3] / "knowledge_pack"
CAPABILITIES_DOC_ID = "capacidades-asistente"


def _parse_sections(content: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    parts = re.split(r"^##\s+", content, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        heading = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if heading and body:
            sections[heading] = body
    return sections


class KnowledgePackProvider(KnowledgeProvider):
    provider_id = "knowledge_pack"
    display_name = "Paquete de conocimiento (Markdown)"

    def is_available(self) -> bool:
        return PACK_ROOT.exists()

    def pack_signature(self) -> float:
        if not PACK_ROOT.exists():
            return 0.0
        latest = 0.0
        for path in PACK_ROOT.rglob("*.md"):
            latest = max(latest, path.stat().st_mtime)
        return latest

    def load_documents(self) -> list[KnowledgeDocument]:
        documents: list[KnowledgeDocument] = []
        if not PACK_ROOT.exists():
            return documents
        for path in sorted(PACK_ROOT.rglob("*.md")):
            if path.name.startswith("."):
                continue
            content = path.read_text(encoding="utf-8")
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = (
                title_match.group(1).strip()
                if title_match
                else path.stem.replace("-", " ").title()
            )
            documents.append(
                KnowledgeDocument(
                    id=path.stem,
                    title=title,
                    category=path.parent.name,
                    path=str(path.relative_to(PACK_ROOT)).replace("\\", "/"),
                    content=content,
                    provider=self.provider_id,
                    sections=_parse_sections(content),
                )
            )
        return documents


def parse_list_section(text: str) -> tuple[str, ...]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return tuple(items)


__all__ = ["KnowledgePackProvider", "PACK_ROOT", "CAPABILITIES_DOC_ID", "parse_list_section"]
