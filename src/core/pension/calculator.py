"""Motor de cálculo pensional colombiano v2 - Ley 797/2003 VIGENTE.

Pipeline completo:
    1. Input: fecha_nacimiento, sexo, semanas, periodos cotizados
    2. Indexar IBC al IPC del periodo de referencia
    3. Calcular IBL segun ventana (10/20/toda la vida)
    4. Validar requisitos (edad + semanas)
    5. Aplicar tasa de reemplazo VIGENTE (Ley 797/2003 con decreciente)
    6. Calcular mesada pensional

Fuentes legales:
- Ley 100/1993 - Sistema General de Pensiones
- Ley 797/2003 Art. 10 - Tasa de reemplazo (vigente)
- Noticia Colpensiones 2024 - Validacion oficial
- Decreto 1158/2020 - Reglamentacion

Reglas clave:
- Edad minima: 62 (hombres), 57 (mujeres)
- Semanas minimas: 1,300 (Ley 797/2003)
- Tasa reemplazo BASE: 55% a 65% (decreciente segun ingreso)
- Incremento: 1.5% por cada 50 semanas sobre 1,300
- Tope maximo: 80% del IBL
- Minimo: 1 SMLMV
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from src.core.pension.ibl import calcular_ibl, ventana_por_semanas
from src.core.pension.ibc import PeriodoCotizacion
from src.core.pension.ipc import indexar_ibc, cargar_ipc
from src.core.pension.legislacion import (
    calcular_tasa_reemplazo_vigente,
    SMLMV_HISTORICO,
)


# === Constantes legales ===
EDAD_JUBILACION_HOMBRES = 62
EDAD_JUBILACION_MUJERES = 57
SEMANAS_MINIMAS = 1300

# Ventana para calculo del IBL segun Ley 797/2003 Art. 18
VENTANAS_IBL = {
    # (semanas_min, semanas_max): ventana en anios
    (0, 1300): None,        # No califica
    (1300, 1800): 10,        # Ultimos 10 anios
    (1800, 2200): 20,        # Ultimos 20 anios
    (2200, 99999): None,     # Toda la vida laboral
}


@dataclass(frozen=True)
class PensionInput:
    """Input completo para calculo de pension."""
    fecha_nacimiento: date
    sexo: Literal["M", "F"]
    semanas_cotizadas: int
    periodos: list[PeriodoCotizacion]
    regimen: Literal["LEY_100_1993", "LEY_797_2003"] = "LEY_797_2003"
    fecha_referencia_ibl: date | None = None  # Default: hoy
    usar_ipc: bool = True  # Si indexar IBC


@dataclass(frozen=True)
class PensionResult:
    """Output del calculo."""
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
    fecha_referencia: str
    observaciones: list[str] = field(default_factory=list)


def calcular_edad(fecha_nacimiento: date, referencia: date | None = None) -> int:
    """Calcula edad en anios cumplidos."""
    if referencia is None:
        referencia = date.today()
    edad = referencia.year - fecha_nacimiento.year
    if (referencia.month, referencia.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def obtener_edad_jubilacion(sexo: str) -> int:
    return EDAD_JUBILACION_HOMBRES if sexo == "M" else EDAD_JUBILACION_MUJERES


def nombre_ventana(semanas: int) -> str:
    """Nombre legible de la ventana de IBC utilizada."""
    ventana = ventana_por_semanas(semanas)
    if ventana is None:
        return "toda_vida_laboral"
    return f"ultimos_{ventana}_años"


def indexar_periodos(
    periodos: list[PeriodoCotizacion],
    fecha_referencia: date,
) -> list[PeriodoCotizacion]:
    """Indexa cada periodo de cotizacion al IPC de la fecha de referencia."""
    periodos_idx = []
    for p in periodos:
        # Usar el ULTIMO mes del periodo como referencia
        fecha_fin_mes = date(p.fecha_fin.year, p.fecha_fin.month, 1)
        ibc_idx = indexar_ibc(p.ibc, fecha_fin_mes, fecha_referencia)
        periodos_idx.append(PeriodoCotizacion(
            fecha_inicio=p.fecha_inicio,
            fecha_fin=p.fecha_fin,
            ibc=ibc_idx,
        ))
    return periodos_idx


def calcular_pension(input_data: PensionInput) -> PensionResult:
    """Pipeline principal de calculo con IPC + legislacion vigente."""
    fecha_ref = input_data.fecha_referencia_ibl or date.today()

    # 1. Indexar IBC al IPC si esta habilitado
    if input_data.usar_ipc:
        periodos_para_ibl = indexar_periodos(input_data.periodos, fecha_ref)
    else:
        periodos_para_ibl = input_data.periodos

    # 2. Calcular IBL segun ventana legal
    ibl = calcular_ibl(periodos_para_ibl, input_data.semanas_cotizadas)
    ventana = nombre_ventana(input_data.semanas_cotizadas)

    # 3. Validar requisitos
    edad = calcular_edad(input_data.fecha_nacimiento, fecha_ref)
    edad_req = obtener_edad_jubilacion(input_data.sexo)
    cumple_edad = edad >= edad_req
    cumple_semanas = input_data.semanas_cotizadas >= SEMANAS_MINIMAS
    tiene_derecho = cumple_edad and cumple_semanas

    # 4. Calcular tasa de reemplazo segun regimen
    if input_data.regimen == "LEY_100_1993":
        from src.core.pension.legislacion import calcular_tasa_ley_100_1993
        calc_tasa = lambda s: calcular_tasa_ley_100_1993(s)
    else:
        calc_tasa = lambda s, ibl=ibl, anio=fecha_ref.year: calcular_tasa_reemplazo_vigente(s, ibl, anio)

    if tiene_derecho:
        tasa = calc_tasa(input_data.semanas_cotizadas)
    else:
        # Si no califica, mostrar tasa proyectada
        tasa = calc_tasa(max(input_data.semanas_cotizadas, SEMANAS_MINIMAS))

    # 4.5. Aplicar tope legal al IBL: 25 SMLMV (Ley 797/2003 Art. 18)
    smlmv_ref = SMLMV_HISTORICO.get(fecha_ref.year, 1_300_000)
    tope_ibl = 25 * smlmv_ref
    ibl_original = ibl
    if ibl > tope_ibl:
        ibl = tope_ibl
        observaciones_temp = []
    else:
        observaciones_temp = []

    # 5. Calcular mesada
    mesada_original = ibl * tasa
    mesada = mesada_original

    # 5.1. Aplicar piso legal: 1 SMLMV (Ley 797/2003 Art. 10)
    # Solo si tiene derecho (cumple edad Y semanas)
    piso_smlmv = smlmv_ref
    piso_aplicado = False
    if tiene_derecho and mesada < piso_smlmv and ibl_original > 0:
        mesada = float(piso_smlmv)
        piso_aplicado = True

    # 6. Generar observaciones
    observaciones = []
    if ibl_original > tope_ibl:
        observaciones.append(
            f"IBL calculado (${ibl_original:,.0f}) superaba el tope legal de 25 SMLMV "
            f"(${tope_ibl:,.0f}). Se ajusto al tope (Ley 797/2003 Art. 18)."
        )
    if piso_aplicado:
        observaciones.append(
            f"Mesada calculada (${mesada_original:,.0f}) inferior al piso legal de 1 SMLMV "
            f"(${piso_smlmv:,.0f}). Se ajusto al piso (Ley 797/2003 Art. 10)."
        )
    if not cumple_edad:
        observaciones.append(
            f"Edad actual: {edad} años. Requiere {edad_req}. "
            f"Faltan {edad_req - edad} años."
        )
    if not cumple_semanas:
        observaciones.append(
            f"Semanas: {input_data.semanas_cotizadas}. "
            f"Minimo {SEMANAS_MINIMAS}. "
            f"Faltan {SEMANAS_MINIMAS - input_data.semanas_cotizadas}."
        )
    if ibl_original == 0:
        observaciones.append(
            "Sin periodos de cotizacion, el IBL es $0. "
            "Suba su historia laboral."
        )

    return PensionResult(
        tiene_derecho=tiene_derecho,
        semanas_cotizadas=input_data.semanas_cotizadas,
        semanas_faltantes=max(0, SEMANAS_MINIMAS - input_data.semanas_cotizadas),
        edad_actual=edad,
        edad_jubilacion=edad_req,
        ibl_calculado=ibl,
        ventana_utilizada=ventana,
        tasa_reemplazo=tasa,
        mesada_pensional=mesada,
        regimen_aplicable=input_data.regimen,
        fecha_referencia=fecha_ref.isoformat(),
        observaciones=observaciones,
    )
