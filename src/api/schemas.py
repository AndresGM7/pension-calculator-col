"""Pydantic v2 schemas for pension calculation API."""
from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Sexo(str, Enum):
    MASCULINO = "M"
    FEMENINO = "F"


class Regimen(str, Enum):
    LEY_100_1993 = "LEY_100_1993"
    LEY_797_2003 = "LEY_797_2003"


class PeriodoCotizacionSchema(BaseModel):
    """Un periodo donde la persona cotizo."""
    model_config = ConfigDict(json_schema_extra={"example": {
        "fecha_inicio": "1984-08-28",
        "fecha_fin": "1985-01-16",
        "ibc": 14610,
    }})

    fecha_inicio: date
    fecha_fin: date
    ibc: float = Field(
        ...,
        gt=0,
        le=100_000_000,  # 100M COP/mes cubre topes legales (25 SMLMV * 4M = ~100M)
        description="Salario mensual sobre el que cotizo (COP)",
    )

    @field_validator("fecha_fin")
    @classmethod
    def validar_fecha_fin_posterior(cls, v: date, info) -> date:
        """Valida que fecha_fin >= fecha_inicio."""
        fecha_inicio = info.data.get("fecha_inicio")
        if fecha_inicio and v < fecha_inicio:
            raise ValueError(
                f"fecha_fin ({v}) debe ser posterior o igual a fecha_inicio ({fecha_inicio})"
            )
        return v

    @field_validator("fecha_inicio")
    @classmethod
    def validar_fecha_inicio_no_futura(cls, v: date) -> date:
        """Valida que fecha_inicio no este en el futuro lejano."""
        if v > date.today():
            # Solo permitir fechas futuras hasta fin de anio actual
            from datetime import date as d
            fin_anio = d(v.year, 12, 31)
            if v > fin_anio:
                raise ValueError(
                    f"fecha_inicio ({v}) no puede estar en el futuro lejano"
                )
        return v


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
        "ventana_utilizada": "ultimos_10_años",
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


class EscenarioRAISSchema(BaseModel):
    """Escenario de rentabilidad para RAIS."""

    nombre: str
    rentabilidad_anual: float
    tipo_fondo: str
    descripcion: str
    saldo_final: float
    mesada_vitalicia: float
    mesada_retiro_programado: float


class ComparacionRegimenesSchema(BaseModel):
    """Response de comparación RPM vs RAIS."""

    fecha_nacimiento: str
    sexo: str
    semanas_cotizadas: int
    edad_actual: int
    edad_jubilacion_rpm: int
    edad_jubilacion_rais: int

    rpm_mesada: float
    rpm_ibl: float
    rpm_tasa: float
    rpm_tiene_derecho: bool

    rais_mesada_vitalicia: float
    rais_mesada_retiro_programado: float
    rais_saldo_final: float
    rais_escenario_usado: str
    rais_escenarios: list[EscenarioRAISSchema]

    diferencia_mensual: float
    diferencia_porcentual: float
    regimen_recomendado: Literal["RPM", "RAIS", "INDECISO"]

    ventajas_rpm: list[str]
    ventajas_rais: list[str]
    observaciones: list[str]


class PuntoProyeccionSchema(BaseModel):
    """Estado proyectado en un momento del tiempo."""

    anios_desde_hoy: int
    fecha: str
    edad: int
    semanas_cotizadas_proyectadas: int
    ibl_proyectado: float
    tasa_reemplazo_proyectada: float
    mesada_rpm_proyectada: float
    saldo_rais_proyectado: float
    mesada_rais_vitalicia: float
    mesada_rais_retiro_programado: float
    notas: list[str]


class ProyeccionInputSchema(BaseModel):
    """Input para proyeccion a multiples horizontes."""

    fecha_nacimiento: date
    sexo: str = Field(pattern="^[MF]$")
    semanas_cotizadas: int = Field(ge=0, le=10000)
    periodos: list[dict] = Field(default_factory=list)
    escenario: Literal["Conservador", "Base", "Agresivo"] = "Base"
    horizonte_anios: list[int] = Field(default_factory=lambda: [5, 10, 15, 20])
    regimen_rpm: Literal["LEY_100_1993", "LEY_797_2003"] = "LEY_797_2003"
    tipo_fondo_rais: Literal["Conservador", "Moderado", "Mayor_Riesgo"] = "Moderado"


class ProyeccionCompletaSchema(BaseModel):
    """Proyeccion completa a multiples horizontes."""

    fecha_calculo: str
    fecha_nacimiento: str
    sexo: str
    edad_actual: int
    semanas_cotizadas_actuales: int
    horizonte_anios: list[int]
    escenario: str
    descripcion_escenario: str
    puntos: list[PuntoProyeccionSchema]


class CompararEscenariosInputSchema(BaseModel):
    """Input para comparar 3 escenarios macro."""

    fecha_nacimiento: date
    sexo: str = Field(pattern="^[MF]$")
    semanas_cotizadas: int = Field(ge=0, le=10000)
    periodos: list[dict] = Field(default_factory=list)
    horizonte_anios: list[int] = Field(default_factory=lambda: [5, 10, 15, 20])
    regimen_rpm: Literal["LEY_100_1993", "LEY_797_2003"] = "LEY_797_2003"
    tipo_fondo_rais: Literal["Conservador", "Moderado", "Mayor_Riesgo"] = "Moderado"


class CompararEscenariosResponseSchema(BaseModel):
    """Response con 3 proyecciones (Conservador, Base, Agresivo)."""

    fecha_calculo: str
    fecha_nacimiento: str
    escenarios: dict[str, ProyeccionCompletaSchema]
