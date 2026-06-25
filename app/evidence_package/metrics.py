class EvidencePackageMetrics:
    evidence_packages_total: int = 0
    total_package_size: int = 0
    total_evidence_items: int = 0
    total_confidence: float = 0.0
    missing_evidence: int = 0
    package_build_time: float = 0.0
    last_build_time: float = 0.0

    missing_evidence_packages: list[dict] = []
    missing_eko_packages: list[dict] = []
    missing_ero_packages: list[dict] = []
    invalid_confidence_packages: list[dict] = []
    duplicate_evidence_packages: list[dict] = []
    inconsistent_limitations_packages: list[dict] = []

    @classmethod
    def record_build(
        cls,
        *,
        package_id: str,
        package_size: int,
        evidence_items: int,
        confidence: float,
        build_time_seconds: float,
        has_evidence: bool,
        missing_eko: bool,
        missing_ero: bool,
        invalid_confidence: bool,
        duplicate_evidence: bool,
        inconsistent_limitations: bool,
    ) -> None:
        cls.evidence_packages_total += 1
        cls.total_package_size += package_size
        cls.total_evidence_items += evidence_items
        cls.total_confidence += confidence
        cls.last_build_time = build_time_seconds
        cls.package_build_time = build_time_seconds

        if not has_evidence:
            cls.missing_evidence += 1
            cls.missing_evidence_packages.append({"package_id": package_id})
        if missing_eko:
            cls.missing_eko_packages.append({"package_id": package_id})
        if missing_ero:
            cls.missing_ero_packages.append({"package_id": package_id})
        if invalid_confidence:
            cls.invalid_confidence_packages.append({"package_id": package_id})
        if duplicate_evidence:
            cls.duplicate_evidence_packages.append({"package_id": package_id})
        if inconsistent_limitations:
            cls.inconsistent_limitations_packages.append({"package_id": package_id})

    @classmethod
    def average_package_size(cls) -> float:
        if cls.evidence_packages_total <= 0:
            return 0.0
        return round(cls.total_package_size / cls.evidence_packages_total, 2)

    @classmethod
    def average_evidence_items(cls) -> float:
        if cls.evidence_packages_total <= 0:
            return 0.0
        return round(cls.total_evidence_items / cls.evidence_packages_total, 2)

    @classmethod
    def average_confidence(cls) -> float:
        if cls.evidence_packages_total <= 0:
            return 0.0
        return round(cls.total_confidence / cls.evidence_packages_total, 4)

    @classmethod
    def snapshot(cls) -> dict:
        return {
            "evidence_packages_total": cls.evidence_packages_total,
            "average_package_size": cls.average_package_size(),
            "average_evidence_items": cls.average_evidence_items(),
            "average_confidence": cls.average_confidence(),
            "average_evidence_confidence": cls.average_confidence(),
            "missing_evidence": cls.missing_evidence,
            "package_build_time": cls.package_build_time,
        }

    @classmethod
    def health_issues(cls) -> dict:
        return {
            "missing_evidence": cls.missing_evidence_packages[-100:],
            "missing_eko": cls.missing_eko_packages[-100:],
            "missing_ero": cls.missing_ero_packages[-100:],
            "invalid_confidence": cls.invalid_confidence_packages[-100:],
            "duplicate_evidence": cls.duplicate_evidence_packages[-100:],
            "inconsistent_limitations": cls.inconsistent_limitations_packages[-100:],
        }

    @classmethod
    def reset_for_tests(cls) -> None:
        cls.evidence_packages_total = 0
        cls.total_package_size = 0
        cls.total_evidence_items = 0
        cls.total_confidence = 0.0
        cls.missing_evidence = 0
        cls.package_build_time = 0.0
        cls.last_build_time = 0.0
        cls.missing_evidence_packages = []
        cls.missing_eko_packages = []
        cls.missing_ero_packages = []
        cls.invalid_confidence_packages = []
        cls.duplicate_evidence_packages = []
        cls.inconsistent_limitations_packages = []
