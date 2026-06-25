from collections import Counter


class SemanticIntentMetrics:
    semantic_parses: int = 0
    execution_plans: int = 0
    verb_distribution: Counter = Counter()
    confidence_total: float = 0.0
    successful_plans: int = 0
    unknown_verbs: int = 0
    ambiguous_objects: list[dict] = []
    incomplete_plans: list[dict] = []
    incompatible_strategies: list[dict] = []
    invalid_confidence: list[dict] = []

    @classmethod
    def record_parse(cls, *, verb_id: str | None, confidence: float) -> None:
        cls.semantic_parses += 1
        cls.confidence_total += confidence
        if verb_id:
            cls.verb_distribution[verb_id] += 1
        else:
            cls.unknown_verbs += 1

    @classmethod
    def record_plan(
        cls,
        *,
        plan_id: str,
        verb_id: str | None,
        confidence: float,
        incomplete: bool,
        incompatible: bool,
        ambiguous_objects: bool,
    ) -> None:
        cls.execution_plans += 1
        if not incomplete and not incompatible and 0 <= confidence <= 1:
            cls.successful_plans += 1
        else:
            if incomplete:
                cls.incomplete_plans.append({"plan_id": plan_id})
            if incompatible:
                cls.incompatible_strategies.append({"plan_id": plan_id})
        if ambiguous_objects:
            cls.ambiguous_objects.append({"plan_id": plan_id})
        if confidence < 0 or confidence > 1:
            cls.invalid_confidence.append({"plan_id": plan_id, "confidence": confidence})

    @classmethod
    def average_semantic_confidence(cls) -> float:
        if cls.semantic_parses <= 0:
            return 0.0
        return round(cls.confidence_total / cls.semantic_parses, 4)

    @classmethod
    def planner_success_rate(cls) -> float:
        if cls.execution_plans <= 0:
            return 0.0
        return round(cls.successful_plans / cls.execution_plans, 4)

    @classmethod
    def snapshot(cls) -> dict:
        return {
            "semantic_parses": cls.semantic_parses,
            "execution_plans": cls.execution_plans,
            "verb_distribution": dict(cls.verb_distribution),
            "average_semantic_confidence": cls.average_semantic_confidence(),
            "planner_success_rate": cls.planner_success_rate(),
            "unknown_verbs": cls.unknown_verbs,
        }

    @classmethod
    def health_issues(cls) -> dict:
        return {
            "unknown_verbs_count": cls.unknown_verbs,
            "ambiguous_objects": cls.ambiguous_objects[-100:],
            "incomplete_plans": cls.incomplete_plans[-100:],
            "incompatible_strategies": cls.incompatible_strategies[-100:],
            "invalid_confidence": cls.invalid_confidence[-100:],
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.semantic_parses = 0
        cls.execution_plans = 0
        cls.verb_distribution = Counter()
        cls.confidence_total = 0.0
        cls.successful_plans = 0
        cls.unknown_verbs = 0
        cls.ambiguous_objects = []
        cls.incomplete_plans = []
        cls.incompatible_strategies = []
        cls.invalid_confidence = []
