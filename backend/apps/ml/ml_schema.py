from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence


@dataclass(frozen=True)
class FeatureSchema:
    columns: List[str]


class FeatureSchemaMismatch(Exception):
    pass


def get_training_feature_schema() -> FeatureSchema:
    """Schema fijo usado por train.py.

    No inspeccionamos internamente el train.py por restricción de no reemplazar.
    """
    return FeatureSchema(
        columns=[
            "edad",
            "imc",
            "presion_sistolica",
            "presion_diastolica",
            "glucosa",
            "colesterol",
        ]
    )


def validate_feature_schema(training: Sequence[str], prediction: Sequence[str]) -> None:
    """Valida que el schema sea compatible.

    - nombres
    - cantidad
    - orden
    """
    training_list = list(training)
    prediction_list = list(prediction)

    if len(training_list) != len(prediction_list):
        raise FeatureSchemaMismatch(
            f"Cantidad de features distinta: train={len(training_list)} pred={len(prediction_list)}"
        )

    if training_list != prediction_list:
        raise FeatureSchemaMismatch(
            "Feature schema mismatch. "
            f"train={training_list} pred={prediction_list}"
        )


def prediction_feature_schema_from_patient_data(patient_data: Dict[str, Any]) -> List[str]:
    # predict.py construye df_input con un order fijo (vericción implícita)
    # Lo repetimos aquí para validar contra el training.
    return [
        "edad",
        "imc",
        "presion_sistolica",
        "presion_diastolica",
        "glucosa",
        "colesterol",
    ]

