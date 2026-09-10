"""Shared field names and schema constants for NASA CRM."""

from typing import Final

SCHEMA_VERSION: Final = 1
MANIFEST_NAME: Final = "manifest.json"

COORDINATE_FIELDS: Final = ("CoordinateX", "CoordinateY", "CoordinateZ")
NORMAL_FIELDS: Final = ("NormalX", "NormalY", "NormalZ")
CONDITION_FIELDS: Final = (
    "Mach",
    "AlphaMean",
    "aileronInboard",
    "aileronOutboard",
    "htp",
    "elevator",
)
LABEL_FIELDS: Final = ("PressureCoefficient", "cfx", "cfy", "cfz")
GLOBAL_TARGET_FIELDS: Final = ("c_d", "c_l", "c_my")
INPUT_FIELDS: Final = COORDINATE_FIELDS + NORMAL_FIELDS + CONDITION_FIELDS
AREA_FIELD: Final = "Surface"

REQUIRED_DATASETS: Final = set(COORDINATE_FIELDS + NORMAL_FIELDS + LABEL_FIELDS + (AREA_FIELD,))
REQUIRED_ATTRIBUTES: Final = set(CONDITION_FIELDS + GLOBAL_TARGET_FIELDS)
