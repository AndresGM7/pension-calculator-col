"""Pension calculation endpoints."""
from datetime import date

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from src.api.schemas import PensionInputSchema, PensionResultSchema
from src.core.pension.calculator import (
    EDAD_JUBILACION_HOMBRES,
    EDAD_JUBILACION_MUJERES,
    SEMANAS_MINIMAS,
    PensionInput,
    calcular_edad,
    calcular_pension,
    obtener_edad_jubilacion,
)
from src.core.pension.ibc import PeriodoCotizacion

router = APIRouter()


@router.post(
    "/calcular",
    response_model=PensionResultSchema,
    status_code=status.HTTP_200_OK,
    summary="Calcular mesada pensional",
    description="Calcula la mesada pensional colombiana segun Ley 100/1993 o Ley 797/2003",
)
async def calcular_mesada(input_data: PensionInputSchema) -> PensionResultSchema:
    """Calcula la pension de vejez de una persona."""
    periodos = [
        PeriodoCotizacion(
            fecha_inicio=p.fecha_inicio,
            fecha_fin=p.fecha_fin,
            ibc=p.ibc,
        )
        for p in input_data.periodos
    ]

    pension_input = PensionInput(
        fecha_nacimiento=input_data.fecha_nacimiento,
        sexo=input_data.sexo.value,
        semanas_cotizadas=input_data.semanas_cotizadas,
        periodos=periodos,
        regimen=input_data.regimen.value,
    )

    result = calcular_pension(pension_input)

    return PensionResultSchema(
        tiene_derecho=result.tiene_derecho,
        semanas_cotizadas=result.semanas_cotizadas,
        semanas_faltantes=result.semanas_faltantes,
        edad_actual=result.edad_actual,
        edad_jubilacion=result.edad_jubilacion,
        ibl_calculado=result.ibl_calculado,
        ventana_utilizada=result.ventana_utilizada,
        tasa_reemplazo=result.tasa_reemplazo,
        mesada_pensional=result.mesada_pensional,
        regimen_aplicable=result.regimen_aplicable,
        observaciones=result.observaciones,
    )


class ProyeccionInputSchema(BaseModel):
    """Input para proyeccion a futuro."""
    fecha_nacimiento: date
    sexo: str = Field(pattern="^[MF]$")
    semanas_cotizadas: int = Field(ge=0)
    periodos: list[dict] = Field(default_factory=list)
    regimen: str = Field(default="LEY_797_2003", pattern="^LEY_(100_1993|797_2003)$")


class ProyeccionResultadoSchema(BaseModel):
    """Resultado de proyeccion."""
    fecha_nacimiento: str
    edad_actual: int
    edad_jubilacion: int
    semanas_cotizadas: int
    semanas_faltantes: int
    anos_faltantes_por_edad: int
    anos_faltantes_por_semanas: float
    semanas_necesarias_para_jubilarse: int
    fecha_estimada_jubilacion: str
    tasa_reemplazo_alcanzable: float
    mesada_proyectada: float
    recomendaciones: list[str]


@router.post(
    "/proyectar",
    response_model=ProyeccionResultadoSchema,
    summary="Proyectar cuando podra jubilarse",
    description="Calcula cuantos anos/semanas faltan para alcanzar el derecho a pension",
)
async def proyectar_jubilacion(input_data: ProyeccionInputSchema) -> ProyeccionResultadoSchema:
    """Proyecta el momento en que la persona podra jubilarse."""
    hoy = date.today()
    edad_actual = calcular_edad(input_data.fecha_nacimiento, hoy)
    edad_req = obtener_edad_jubilacion(input_data.sexo)

    anos_por_edad = max(0, edad_req - edad_actual)

    semanas_faltantes = max(0, SEMANAS_MINIMAS - input_data.semanas_cotizadas)
    anos_por_semanas = semanas_faltantes / 50.0

    anos_totales = max(anos_por_edad, anos_por_semanas)
    anio_jubilacion = hoy.year + int(anos_totales) + 1
    fecha_estimada = date(anio_jubilacion, 1, 1)

    periodos_convertidos = []
    for p in input_data.periodos:
        periodos_convertidos.append(
            PeriodoCotizacion(
                fecha_inicio=p["fecha_inicio"] if isinstance(p["fecha_inicio"], date) else date.fromisoformat(p["fecha_inicio"]),
                fecha_fin=p["fecha_fin"] if isinstance(p["fecha_fin"], date) else date.fromisoformat(p["fecha_fin"]),
                ibc=float(p["ibc"]),
            )
        )

    anos_cotizando_proyectados = max(0, anos_por_semanas)
    semanas_proyectadas = input_data.semanas_cotizadas + int(anos_cotizando_proyectados * 50)

    pension_input = PensionInput(
        fecha_nacimiento=input_data.fecha_nacimiento,
        sexo=input_data.sexo,
        semanas_cotizadas=semanas_proyectadas,
        periodos=periodos_convertidos,
        regimen=input_data.regimen,
    )
    result = calcular_pension(pension_input)

    recomendaciones = []
    if semanas_faltantes > 0:
        recomendaciones.append(
            f"Necesita {semanas_faltantes} semanas mas "
            f"(~{semanas_faltantes/50:.1f} anos cotizando)."
        )
        recomendaciones.append(
            "Cotizar de forma continua es la forma mas eficiente de sumar semanas."
        )
    if anos_por_edad > 0:
        recomendaciones.append(
            f"Le faltan {anos_por_edad} anos para alcanzar la edad de jubilacion ({edad_req})."
        )
    if semanas_faltantes == 0 and anos_por_edad == 0:
        recomendaciones.append(
            "Ya cumple los requisitos. Puede solicitar su pension ante Colpensiones/AFP."
        )
    if not input_data.periodos:
        recomendaciones.append(
            "Sin periodos de cotizacion, el IBL se calcula como $0. "
            "Suba su historia laboral para un calculo preciso."
        )

    return ProyeccionResultadoSchema(
        fecha_nacimiento=input_data.fecha_nacimiento.isoformat(),
        edad_actual=edad_actual,
        edad_jubilacion=edad_req,
        semanas_cotizadas=input_data.semanas_cotizadas,
        semanas_faltantes=semanas_faltantes,
        anos_faltantes_por_edad=anos_por_edad,
        anos_faltantes_por_semanas=anos_por_semanas,
        semanas_necesarias_para_jubilarse=semanas_faltantes,
        fecha_estimada_jubilacion=fecha_estimada.isoformat(),
        tasa_reemplazo_alcanzable=result.tasa_reemplazo,
        mesada_proyectada=result.mesada_pensional,
        recomendaciones=recomendaciones,
    )


@router.get(
    "/info/regimenes",
    summary="Informacion sobre regimenes legales",
)
async def info_regimenes():
    """Devuelve resumen de los regimenes legales colombianos."""
    return {
        "ley_100_1993": {
            "nombre": "Sistema General de Pensiones",
            "semanas_minimas": 1000,
            "tasa_base": "65% del IBL + 1.5% por 50 semanas adicionales, max 80%",
            "edad_jubilacion": {"hombres": EDAD_JUBILACION_HOMBRES, "mujeres": EDAD_JUBILACION_MUJERES},
        },
        "ley_797_2003": {
            "nombre": "Reforma de la Ley 100",
            "semanas_minimas": SEMANAS_MINIMAS,
            "tasa_base": "Tabla escalonada de 40% a 80% del IBL segun semanas",
            "edad_jubilacion": {"hombres": EDAD_JUBILACION_HOMBRES, "mujeres": EDAD_JUBILACION_MUJERES},
            "fuente": "Guia AMV Fondos de Pensiones Operador 2020",
        },
    }
