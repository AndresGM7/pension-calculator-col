"""Pension calculation endpoints."""
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from src.api.dependencies import require_feature

from src.api.schemas import (
    ComparacionRegimenesSchema,
    CompararEscenariosResponseSchema,
    EscenarioRAISSchema,
    PensionInputSchema,
    PensionResultSchema,
    ProyeccionCompletaSchema,
    PuntoProyeccionSchema,
)
from src.core.pension.calculator import (
    EDAD_JUBILACION_HOMBRES,
    EDAD_JUBILACION_MUJERES,
    SEMANAS_MINIMAS,
    PensionInput,
    calcular_edad,
    calcular_pension,
    obtener_edad_jubilacion,
)
from src.core.pension.comparacion import comparar_regimenes
from src.core.pension.ibc import PeriodoCotizacion

router = APIRouter()


@router.post(
    "/calcular",
    response_model=PensionResultSchema,
    status_code=status.HTTP_200_OK,
    summary="Calcular mesada pensional",
    description="Calcula la mesada pensional colombiana segun Ley 100/1993 o Ley 797/2003",
)
async def calcular_mesada(
    input_data: PensionInputSchema,
    _user_tier: str = Depends(require_feature("calcular_rpm")),
) -> PensionResultSchema:
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
    description="Calcula cuantos años/semanas faltan para alcanzar el derecho a pension",
)
async def proyectar_jubilacion(
    input_data: ProyeccionInputSchema,
    _user_tier: str = Depends(require_feature("calcular_rpm")),
) -> ProyeccionResultadoSchema:
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
            f"(~{semanas_faltantes/50:.1f} años cotizando)."
        )
        recomendaciones.append(
            "Cotizar de forma continua es la forma mas eficiente de sumar semanas."
        )
    if anos_por_edad > 0:
        recomendaciones.append(
            f"Le faltan {años_por_edad} años para alcanzar la edad de jubilacion ({edad_req})."
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


class ComparacionInputSchema(BaseModel):
    """Input para comparación RPM vs RAIS."""
    fecha_nacimiento: date
    sexo: str = Field(pattern="^[MF]$")
    semanas_cotizadas: int = Field(ge=0, le=10000)
    periodos: list[dict] = Field(
        default_factory=list,
        description="Historia laboral con IBCs indexados",
    )
    regimen_rpm: Literal["LEY_100_1993", "LEY_797_2003"] = "LEY_797_2003"
    comision_afp: float = Field(default=0.015, ge=0, le=0.10)
    usar_ipc: bool = True


@router.post(
    "/comparar-regimenes",
    response_model=ComparacionRegimenesSchema,
    summary="Comparar RPM (Colpensiones) vs RAIS (AFPs privadas)",
    description="Calcula y compara la pensión esperada en ambos regimenes bajo 3 escenarios de rentabilidad RAIS.",
)
async def comparar_regimenes_endpoint(
    input_data: ComparacionInputSchema,
    _user_tier: str = Depends(require_feature("comparar_regimenes")),
) -> ComparacionRegimenesSchema:
    """Compara pensión esperada en RPM vs RAIS.

    Esta es la funcionalidad DIFERENCIADORA del producto. Permite al usuario
    ver objetivamente cuál régimen le conviene más.
    """
    periodos_convertidos = []
    for p in input_data.periodos:
        periodos_convertidos.append(
            PeriodoCotizacion(
                fecha_inicio=p["fecha_inicio"] if isinstance(p["fecha_inicio"], date) else date.fromisoformat(p["fecha_inicio"]),
                fecha_fin=p["fecha_fin"] if isinstance(p["fecha_fin"], date) else date.fromisoformat(p["fecha_fin"]),
                ibc=float(p["ibc"]),
            )
        )

    resultado = comparar_regimenes(
        fecha_nacimiento=input_data.fecha_nacimiento,
        sexo=input_data.sexo,
        semanas_cotizadas=input_data.semanas_cotizadas,
        periodos=periodos_convertidos,
        regimen_rpm=input_data.regimen_rpm,
        comision_afp=input_data.comision_afp,
        usar_ipc=input_data.usar_ipc,
    )

    return ComparacionRegimenesSchema(
        fecha_nacimiento=resultado.fecha_nacimiento,
        sexo=resultado.sexo,
        semanas_cotizadas=resultado.semanas_cotizadas,
        edad_actual=resultado.edad_actual,
        edad_jubilacion_rpm=resultado.edad_jubilacion_rpm,
        edad_jubilacion_rais=resultado.edad_jubilacion_rais,
        rpm_mesada=resultado.rpm_mesada,
        rpm_ibl=resultado.rpm_ibl,
        rpm_tasa=resultado.rpm_tasa,
        rpm_tiene_derecho=resultado.rpm_tiene_derecho,
        rais_mesada_vitalicia=resultado.rais_mesada_vitalicia,
        rais_mesada_retiro_programado=resultado.rais_mesada_retiro_programado,
        rais_saldo_final=resultado.rais_saldo_final,
        rais_escenario_usado=resultado.rais_escenario_usado,
        rais_escenarios=[EscenarioRAISSchema(**e) for e in resultado.rais_escenarios],
        diferencia_mensual=resultado.diferencia_mensual,
        diferencia_porcentual=resultado.diferencia_porcentual,
        regimen_recomendado=resultado.regimen_recomendado,
        ventajas_rpm=resultado.ventajas_rpm,
        ventajas_rais=resultado.ventajas_rais,
        observaciones=resultado.observaciones,
    )


class ProyeccionEndpointInputSchema(BaseModel):
    fecha_nacimiento: date
    sexo: str = Field(pattern="^[MF]$")
    semanas_cotizadas: int = Field(ge=0, le=10000)
    periodos: list[dict] = Field(default_factory=list)
    escenario: Literal["Conservador", "Base", "Agresivo"] = "Base"
    horizonte_anios: list[int] = Field(default_factory=lambda: [5, 10, 15, 20])
    regimen_rpm: Literal["LEY_100_1993", "LEY_797_2003"] = "LEY_797_2003"
    tipo_fondo_rais: Literal["Conservador", "Moderado", "Mayor_Riesgo"] = "Moderado"


def _convertir_periodos(periodos_dicts: list[dict]) -> list[PeriodoCotizacion]:
    periodos = []
    for p in periodos_dicts:
        periodos.append(
            PeriodoCotizacion(
                fecha_inicio=p["fecha_inicio"] if isinstance(p["fecha_inicio"], date) else date.fromisoformat(p["fecha_inicio"]),
                fecha_fin=p["fecha_fin"] if isinstance(p["fecha_fin"], date) else date.fromisoformat(p["fecha_fin"]),
                ibc=float(p["ibc"]),
            )
        )
    return periodos


@router.post(
    "/proyeccion",
    response_model=ProyeccionCompletaSchema,
    summary="Proyectar pension a multiples horizontes (5, 10, 15, 20 años)",
    description="Calcula como evoluciona la pension esperada bajo un escenario macroeconomico especifico.",
)
async def proyeccion_endpoint(
    input_data: ProyeccionEndpointInputSchema,
    _user_tier: str = Depends(require_feature("proyeccion_5_10_15_20")),
) -> ProyeccionCompletaSchema:
    from src.core.pension.proyecciones import proyectar_pension as _proyectar

    periodos = _convertir_periodos(input_data.periodos)

    resultado = _proyectar(
        fecha_nacimiento=input_data.fecha_nacimiento,
        sexo=input_data.sexo,
        semanas_cotizadas=input_data.semanas_cotizadas,
        periodos=periodos,
        escenario_nombre=input_data.escenario,
        horizonte_anios=input_data.horizonte_anios,
        regimen_rpm=input_data.regimen_rpm,
        tipo_fondo_rais=input_data.tipo_fondo_rais,
    )

    return ProyeccionCompletaSchema(
        fecha_calculo=resultado.fecha_calculo,
        fecha_nacimiento=resultado.fecha_nacimiento,
        sexo=resultado.sexo,
        edad_actual=resultado.edad_actual,
        semanas_cotizadas_actuales=resultado.semanas_cotizadas_actuales,
        horizonte_anios=resultado.horizonte_anios,
        escenario=resultado.escenario,
        descripcion_escenario=resultado.descripcion_escenario,
        puntos=[PuntoProyeccionSchema(**vars(p)) for p in resultado.puntos],
    )


@router.post(
    "/comparar-escenarios",
    response_model=CompararEscenariosResponseSchema,
    summary="Comparar 3 escenarios macroeconomicos",
    description="Proyecta la pension esperada bajo Conservador, Base y Agresivo.",
)
async def comparar_escenarios_endpoint(
    input_data: ProyeccionEndpointInputSchema,
    _user_tier: str = Depends(require_feature("comparar_3_escenarios")),
) -> CompararEscenariosResponseSchema:
    from src.core.pension.proyecciones import comparar_escenarios as _comparar

    periodos = _convertir_periodos(input_data.periodos)

    resultados = _comparar(
        fecha_nacimiento=input_data.fecha_nacimiento,
        sexo=input_data.sexo,
        semanas_cotizadas=input_data.semanas_cotizadas,
        periodos=periodos,
        horizonte_anios=input_data.horizonte_anios,
        regimen_rpm=input_data.regimen_rpm,
        tipo_fondo_rais=input_data.tipo_fondo_rais,
    )

    return CompararEscenariosResponseSchema(
        fecha_calculo=list(resultados.values())[0].fecha_calculo,
        fecha_nacimiento=list(resultados.values())[0].fecha_nacimiento,
        escenarios={
            nombre: ProyeccionCompletaSchema(
                fecha_calculo=r.fecha_calculo,
                fecha_nacimiento=r.fecha_nacimiento,
                sexo=r.sexo,
                edad_actual=r.edad_actual,
                semanas_cotizadas_actuales=r.semanas_cotizadas_actuales,
                horizonte_anios=r.horizonte_anios,
                escenario=r.escenario,
                descripcion_escenario=r.descripcion_escenario,
                puntos=[PuntoProyeccionSchema(**vars(p)) for p in r.puntos],
            )
            for nombre, r in resultados.items()
        },
    )
