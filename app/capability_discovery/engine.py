from collections.abc import Callable



from app.capability_discovery.schemas import CapabilityDiscoveryResult

from app.capability_discovery.v2.metrics import CapabilityDiscoveryV2Metrics

from app.capability_discovery.v2.validation import build_validated_v2_discovery_payload

from app.query_engine.query_catalog import DEFAULT_TOP_QUESTIONS



DefaultTopQuestionsProvider = Callable[[int], list[str]]





class CapabilityDiscoveryEngine:

    """Respuesta conversacional breve (v2) sobre capacidades del asistente."""



    def __init__(

        self,

        top_questions_provider: DefaultTopQuestionsProvider | None = None,

    ) -> None:

        _ = top_questions_provider or (lambda limit: list(DEFAULT_TOP_QUESTIONS[:limit]))



    def discover(self) -> CapabilityDiscoveryResult:

        answer, capabilities, example_questions = build_validated_v2_discovery_payload()

        CapabilityDiscoveryV2Metrics.record_response(answer)

        metrics = CapabilityDiscoveryV2Metrics.snapshot()



        return CapabilityDiscoveryResult(

            success=True,

            answer=answer,

            capabilities=capabilities,

            example_questions=example_questions,

            suggestions=None,

            metadata={

                "discovery_success": True,

                "discovery_version": "v2",

                "capabilities_count": len(capabilities),

                "example_questions_count": len(example_questions),

                **metrics,

            },

        )


