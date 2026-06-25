from enum import StrEnum


class BusinessOperation(StrEnum):
    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MAX = "MAX"
    MIN = "MIN"
    TOP = "TOP"
    TREND = "TREND"
    COMPARE = "COMPARE"
    LOOKUP = "LOOKUP"
    SYSTEM_INFO = "SYSTEM_INFO"
    DATA_COVERAGE = "DATA_COVERAGE"
    DATASET_INFO = "DATASET_INFO"
