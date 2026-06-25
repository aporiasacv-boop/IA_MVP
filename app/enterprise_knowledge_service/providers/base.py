from abc import ABC, abstractmethod

from app.enterprise_knowledge_service.schemas import KnowledgeDocument


class KnowledgeProvider(ABC):
    """Contrato para fuentes de conocimiento empresarial."""

    provider_id: str
    display_name: str

    @abstractmethod
    def load_documents(self) -> list[KnowledgeDocument]:
        """Carga documentos desde la fuente."""

    @abstractmethod
    def is_available(self) -> bool:
        """Indica si la fuente está disponible."""


class DatabaseProvider(KnowledgeProvider):
    """Proveedor futuro: base de datos corporativa."""

    provider_id = "database"
    display_name = "Base de datos corporativa"

    def load_documents(self) -> list[KnowledgeDocument]:
        return []

    def is_available(self) -> bool:
        return False


class SharePointProvider(KnowledgeProvider):
    """Proveedor futuro: SharePoint."""

    provider_id = "sharepoint"
    display_name = "Microsoft SharePoint"

    def load_documents(self) -> list[KnowledgeDocument]:
        return []

    def is_available(self) -> bool:
        return False


class PDFProvider(KnowledgeProvider):
    """Proveedor futuro: repositorio de PDFs."""

    provider_id = "pdf"
    display_name = "Repositorio PDF"

    def load_documents(self) -> list[KnowledgeDocument]:
        return []

    def is_available(self) -> bool:
        return False


class DynamicsProvider(KnowledgeProvider):
    """Proveedor futuro: Microsoft Dynamics."""

    provider_id = "dynamics"
    display_name = "Microsoft Dynamics"

    def load_documents(self) -> list[KnowledgeDocument]:
        return []

    def is_available(self) -> bool:
        return False


class ConfluenceProvider(KnowledgeProvider):
    """Proveedor futuro: Atlassian Confluence."""

    provider_id = "confluence"
    display_name = "Atlassian Confluence"

    def load_documents(self) -> list[KnowledgeDocument]:
        return []

    def is_available(self) -> bool:
        return False


PLANNED_PROVIDER_TYPES: tuple[type[KnowledgeProvider], ...] = (
    DatabaseProvider,
    SharePointProvider,
    PDFProvider,
    DynamicsProvider,
    ConfluenceProvider,
)
