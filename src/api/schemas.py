"""Pydantic v2 schemas for pension calculation API."""
from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Sexo(str, Enum):
    MASCULINO = "M"
    FEMENINO = "F"


class Regimen(str, Enum):
    LEY_100_1993 = "LEY_100_1993"
    LEY_797_2003 = "LEY_797_2003"


class PeriodoCotizacionSchema(BaseModel):
    """Un periodo donde la persona cotizó."""
    model_config = ConfigDict(json_schema_extra={"example": {
        "fecha_inicio": "1984-08-28",
        "fecha_fin": "1985-01-16",
        "ibc": 14610,
    }})

    fecha_inicio: date
    fecha_fin: date
    ibc: float = Field(..., gt=0, description="Salario mensual sobre el que cotizó (COP)")


class PensionInputSchema(BaseModel):
    """Request body para cálculo de pensión."""
    model_config = ConfigDict(json_schema_extra={"example": {
        "fecha_nacimiento": "1963-12-06",
        "sexo": "M",
        "semanas_cotizadas": 1800,
        "periodos": [
            {
                "fecha_inicio": "1984-08-28",
                "fecha_fin": "1985-01-16",
                "ibc": 14610,
            }
        ],
        "regimen": "LEY_797_2003",
    }})

    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento (YYYY-MM-DD)")
    sexo: Sexo
    semanas_cotizadas: int = Field(..., ge=0, le=10000)
    periodos: list[PeriodoCotizacionSchema] = Field(
        default_factory=list,
        description="Lista de periodos cotizados (de la historia laboral)",
    )
    regimen: Regimen = Regimen.LEY_797_2003


class PensionResultSchema(BaseModel):
    """Response body del cálculo de pensión."""
    model_config = ConfigDict(json_schema_extra={"example": {
        "tiene_derecho": True,
        "semanas_cotizadas": 1800,
        "semanas_faltantes": 0,
        "edad_actual": 62,
        "edad_jubilacion": 62,
        "ibl_calculado": 250000,
        "ventana_utilizada": "ultimos_10_anos",
        "tasa_reemplazo": 0.68,
        "mesada_pensional": 170000,
        "regimen_aplicable": "LEY_797_2003",
        "observaciones": [],
    }})

    tiene_derecho: bool
    semanas_cotizadas: int
    semanas_faltantes: int
    edad_actual: int
    edad_jubilacion: int
    ibl_calculado: float
    ventana_utilizada: str
    tasa_reemplazo: float
    mesada_pensional: float
    regimen_aplicable: str
    observaciones: list[str]
