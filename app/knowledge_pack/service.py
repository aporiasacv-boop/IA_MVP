from app.enterprise_knowledge_service.schemas import KnowledgeDocument as EKSDocument
from app.knowledge_pack.schemas import KnowledgePackItem, KnowledgePackListResponse, KnowledgePackSearchResponse
from app.enterprise_knowledge_service.service import get_enterprise_knowledge_platform_service


def _to_pack_item(doc: EKSDocument) -> KnowledgePackItem:
    return KnowledgePackItem(
        id=doc.id,
        title=doc.title,
        category=doc.category,
        path=doc.path,
        content=doc.content,
        sections=doc.sections,
    )


class BusinessKnowledgePackService:
    def __init__(self, service=None) -> None:
        self._service = service or get_enterprise_knowledge_platform_service()

    def list_concepts(self) -> KnowledgePackListResponse:
        items = [ _to_pack_item(doc) for doc in self._service._repository.by_category("concepts") ]
        return KnowledgePackListResponse(category="concepts", total=len(items), items=items)

    def list_glossary(self) -> KnowledgePackListResponse:
        items = [ _to_pack_item(doc) for doc in self._service._repository.by_category("glossary") ]
        return KnowledgePackListResponse(category="glossary", total=len(items), items=items)

    def list_faq(self) -> KnowledgePackListResponse:
        items = [ _to_pack_item(doc) for doc in self._service._repository.by_category("faq") ]
        return KnowledgePackListResponse(category="faq", total=len(items), items=items)

    def list_rules(self) -> KnowledgePackListResponse:
        items = [ _to_pack_item(doc) for doc in self._service._repository.by_category("rules") ]
        return KnowledgePackListResponse(category="rules", total=len(items), items=items)

    def list_scenarios(self) -> KnowledgePackListResponse:
        items = [ _to_pack_item(doc) for doc in self._service._repository.by_category("scenarios") ]
        return KnowledgePackListResponse(category="scenarios", total=len(items), items=items)

    def search(self, query: str) -> KnowledgePackSearchResponse:
        result = self._service.search(query)
        items = [_to_pack_item(doc) for doc in result.items]
        return KnowledgePackSearchResponse(query=query, total=len(items), items=items)
