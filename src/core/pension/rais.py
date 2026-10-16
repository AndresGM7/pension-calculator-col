"""Motor de cálculo pensional para RAIS (Régimen de Ahorro Individual con Solidaridad).

IMPLEMENTACIÓN COMPLETA - Sep 2026

Diferencias con RPM:
- RPM (Colpensiones): mesada fija calculada con fórmula legal
- RAIS (AFPs privadas): saldo acumulado + rentabilidad, depende del mercado

Componentes del cálculo:
1. Aportes mensuales: IBC × (% cotización + % adicional) × (1 - comisión AFP)
2. Capitalización mensual: saldo(t+1) = saldo(t) × (1 + r_mensual) + aporte
3. Mesada: saldo_total / meses_de_retiro (basado en tablas de mortalidad)

Fuentes:
- Superintendencia Financiera: rentabilidades históricas por AFP y tipo fondo
- DANE: tablas de mortalidad colombianas
- Ley 100/1993 + Ley 797/2003: regulación general
"""
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal

from src.core.pension.ibc import PeriodoCotizacion


# === Constantes legales (Ley 100/1993 + Ley 797/2003) ===

# Cotización obligatoria total
PORCENTAJE_COTIZACION_OBLIGATORIO = 0.10  # 10% del IBC (3.5% empleado + 6.5% empleador historico, Ley 797)
PORCENTAJE_FSP = 0.01  # Fondo Solidaridad Pensional: 1.0% para IBC > 4 SMLMV
PORCENTAJE_FSP_ALTO = 0.02  # 2.0% para IBC > 16 SMLMV (decreciente en el medio)

# Default conservador para proyección
MESES_RETIRO_DEFAULT = 240  # ~20 años de retiro (simplificación, ver tablas mortalidad abajo)
RENTABILIDAD_ANUAL_DEFAULT = 0.05  # 5% real anual
COMISION_AFP_DEFAULT = 0.015  # 1.5% sobre IBC


# Tabla de mortalidad simplificada (DANE/Supersalud 2018)
# Esperanza de vida adicional al jubilarse (en meses)
# Basada en tablas actuariales colombianas estándar
TABLA_MORTALIDAD_COLOMBIA = {
    # edad_jubilacion: meses_esperados_vida_adicional
    57: 312,  # mujer colombiana 57 años -> ~26 años adicionales
    62: 234,  # hombre colombiano 62 años -> ~19.5 años adicionales (DANE 2018-2023)
    65: 240,  # cualquier sexo 65 años -> ~20 años adicionales
    67: 216,  # ~18 años adicionales
    70: 192,  # ~16 años adicionales
}


@dataclass(frozen=True)
class RaisInput:
    """Inputs para cálculo de pensión bajo RAIS."""
    
    saldo_inicial: float = 0.0
    fecha_saldo_inicial: date | None = None
    porcentaje_cotizacion: float = PORCENTAJE_COTIZACION_OBLIGATORIO
    porcentaje_adicional: float = 0.0
    rentabilidad_anual: float = RENTABILIDAD_ANUAL_DEFAULT
    tipo_fondo: Literal["Conservador", "Moderado", "Mayor_Riesgo"] = "Moderado"
    comision_afp: float = COMISION_AFP_DEFAULT
    modalidad: Literal["renta_vitalicia", "retiro_programado"] = "retiro_programado"


@dataclass(frozen=True)
class RaisResult:
    """Output del cálculo RAIS."""
    
    saldo_final: float
    total_aportes: float
    total_rentabilidad: float
    meses_proyectados: int
    anos_proyectados: float
    mesada_vitalicia: float  # Renta vitalicia (aseguradora paga hasta fallecimiento)
    mesada_retiro_programado: float  # Retiro programado (de tu propio saldo)
    modalidad_recomendada: Literal["renta_vitalicia", "retiro_programado"]
    rentabilidad_efectiva: float
    comision_total_pagada: float
    observaciones: list[str] = field(default_factory=list)


def cargar_rentabilidades() -> dict:
    """Carga las rentabilidades promedio históricas desde JSON.
    
    Returns:
        Dict con estructura:
        {
            "fondos": {
                "Porvenir": {"Conservador": 0.042, "Moderado": 0.055, "Mayor_Riesgo": 0.062},
                ...
            },
            "comisiones_por_afp": {"Porvenir": 0.015, ...}
        }
    """
    ruta = Path(__file__).parent.parent.parent.parent / "data" / "rais_rentabilidades.json"
    if not ruta.exists():
        # Default conservador si no existe el archivo
        return {
            "fondos": {
                "Default": {
                    "Conservador": 0.040,
                    "Moderado": 0.050,
                    "Mayor_Riesgo": 0.060,
                }
            },
            "comisiones_por_afp": {"Default": 0.015},
        }
    
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def calcular_meses_esperados(edad_jubilacion: int) -> int:
    """Calcula meses esperados de vida según tabla de mortalidad colombiana.
    
    Args:
        edad_jubilacion: edad a la que se jubila la persona
    
    Returns:
        Meses esperados de vida adicionales (para cálculo de mesada)
    """
    if edad_jubilacion in TABLA_MORTALIDAD_COLOMBIA:
        return TABLA_MORTALIDAD_COLOMBIA[edad_jubilacion]
    
    # Interpolación lineal para edades no exactas
    edades = sorted(TABLA_MORTALIDAD_COLOMBIA.keys())
    
    if edad_jubilacion < edades[0]:
        # Por debajo del mínimo, asumimos longevidad mayor (sano)
        return TABLA_MORTALIDAD_COLOMBIA[edades[0]]
    
    if edad_jubilacion > edades[-1]:
        # Por encima del máximo, asumimos longevidad menor
        return TABLA_MORTALIDAD_COLOMBIA[edades[-1]]
    
    # Interpolación
    for i in range(len(edades) - 1):
        if edades[i] <= edad_jubilacion <= edades[i + 1]:
            e1, e2 = edades[i], edades[i + 1]
            m1, m2 = TABLA_MORTALIDAD_COLOMBIA[e1], TABLA_MORTALIDAD_COLOMBIA[e2]
            fraccion = (edad_jubilacion - e1) / (e2 - e1)
            return int(m1 + (m2 - m1) * fraccion)
    
    return MESES_RETIRO_DEFAULT


def proyectar_saldo_rais(
    periodos: list[PeriodoCotizacion],
    rais_input: RaisInput,
    fecha_inicio: date,
    fecha_jubilacion: date,
) -> tuple[float, float, float]:
    """Proyecta el saldo acumulado al momento de jubilación con capitalización mensual.
    
    Args:
        periodos: Lista de periodos con IBC
        rais_input: Parámetros del RAIS
        fecha_inicio: Inicio del periodo a proyectar
        fecha_jubilacion: Fecha en que se jubila la persona
    
    Returns:
        (saldo_final, total_aportes, total_comisiones)
    """
    saldo = rais_input.saldo_inicial
    total_aportes = 0.0
    total_comisiones = 0.0
    
    # Tasa mensual equivalente
    r_mensual = (1 + rais_input.rentabilidad_anual) ** (1 / 12) - 1
    
    # Filtrar periodos hasta fecha de jubilación
    periodos_relevantes = [
        p for p in periodos
        if p.fecha_inicio < fecha_jubilacion
    ]
    
    for periodo in periodos_relevantes:
        # Calcular meses del periodo (aproximado: 30.44 días/mes promedio)
        dias = max(1, (periodo.fecha_fin - periodo.fecha_inicio).days)
        meses_periodo = dias / 30.44

        # Calcular FSP (Fondo Solidaridad Pensional) segun nivel de IBC
        # Ley 100/1993 Art. 25 + Decreto 1818/1994:
        #   - IBC <= 4 SMLMV: FSP = 0
        #   - 4 < IBC <= 16 SMLMV: FSP = 1.0% del IBC
        #   - IBC > 16 SMLMV: FSP = 2.0% del IBC
        # El FSP es un aporte ADICIONAL al fondo (no resta del aporte del trabajador)
        # pero reduce el IBC efectivamente cotizado al fondo de pensiones.
        # Para simplificar: el FSP se deduce del aporte que va al fondo de pensiones.
        fsp_pct = 0.0
        smlmv_referencia = 1_560_000  # SMLMV 2026 aprox
        if periodo.ibc > 16 * smlmv_referencia:
            fsp_pct = PORCENTAJE_FSP_ALTO  # 2.0%
        elif periodo.ibc > 4 * smlmv_referencia:
            fsp_pct = PORCENTAJE_FSP  # 1.0%

        # Aporte bruto mensual al fondo (despues de deducir FSP)
        porcentaje_total = (
            rais_input.porcentaje_cotizacion
            + rais_input.porcentaje_adicional
            - fsp_pct
        )
        aporte_bruto = periodo.ibc * porcentaje_total

        # Comisión AFP (sobre IBC, no sobre aporte)
        comision_mensual = periodo.ibc * rais_input.comision_afp

        # Aporte neto después de comisión
        aporte_neto = aporte_bruto - comision_mensual

        if aporte_neto <= 0:
            # Comisión excede aporte (raro pero posible con IBC muy bajo)
            continue

        # Capitalización mes a mes
        for _ in range(int(meses_periodo)):
            saldo = saldo * (1 + r_mensual) + aporte_neto
            total_aportes += aporte_neto
            total_comisiones += comision_mensual

        # Meses parciales (si quedan días sueltos)
        meses_restantes = meses_periodo - int(meses_periodo)
        if meses_restantes > 0:
            saldo = saldo * (1 + r_mensual * meses_restantes) + aporte_neto * meses_restantes
            total_aportes += aporte_neto * meses_restantes
            total_comisiones += comision_mensual * meses_restantes

    return saldo, total_aportes, total_comisiones


def calcular_mesada_rais(
    saldo_final: float,
    edad_jubilacion: int,
    sexo: Literal["M", "F"],
    modalidad: Literal["renta_vitalicia", "retiro_programado"] = "retiro_programado",
) -> tuple[float, float]:
    """Calcula la mesada mensual esperada bajo RAIS.
    
    Args:
        saldo_final: Saldo acumulado al jubilarse
        edad_jubilacion: Edad al jubilarse (afecta meses de retiro)
        sexo: M o F (afecta ligeramente la tabla de mortalidad)
        modalidad: "renta_vitalicia" o "retiro_programado"
    
    Returns:
        (mesada_mensual, meses_duracion)
    """
    meses = calcular_meses_esperados(edad_jubilacion)
    
    if modalidad == "renta_vitalicia":
        # Renta vitalicia: la aseguradora cobra ~3-5% del saldo por administrar la renta
        # Asumimos 4% como default
        factor_administracion = 0.96
        saldo_util = saldo_final * factor_administracion
        return (saldo_util / meses, meses)
    
    # Retiro programado: divide el saldo entre meses esperados
    return (saldo_final / meses, meses)


def calcular_pension_rais(
    periodos: list[PeriodoCotizacion],
    rais_input: RaisInput,
    fecha_nacimiento: date,
    sexo: Literal["M", "F"],
    fecha_calculo: date | None = None,
) -> RaisResult:
    """Pipeline principal de cálculo RAIS.
    
    Args:
        periodos: Historia laboral
        rais_input: Parámetros del RAIS
        fecha_nacimiento: Fecha de nacimiento de la persona
        sexo: M o F
        fecha_calculo: Fecha de referencia para cálculo (default: hoy)
    
    Returns:
        RaisResult con todos los valores calculados
    """
    if fecha_calculo is None:
        fecha_calculo = date.today()
    
    # Calcular edad de jubilación según sexo
    if sexo == "M":
        edad_jubilacion = 62
    else:
        edad_jubilacion = 57
    
    # Calcular fecha de jubilación
    anios_hasta_jubilacion = max(0, edad_jubilacion - calcular_edad_simple(fecha_nacimiento, fecha_calculo))
    fecha_jubilacion = date(
        fecha_calculo.year + anios_hasta_jubilacion,
        fecha_nacimiento.month,
        fecha_nacimiento.day,
    )
    
    # Proyectar saldo
    saldo_final, total_aportes, total_comisiones = proyectar_saldo_rais(
        periodos, rais_input, fecha_calculo, fecha_jubilacion
    )
    
    # Calcular mesadas
    mesada_vitalicia, meses_v = calcular_mesada_rais(
        saldo_final, edad_jubilacion, sexo, "renta_vitalicia"
    )
    mesada_retiro, meses_rp = calcular_mesada_rais(
        saldo_final, edad_jubilacion, sexo, "retiro_programado"
    )
    
    # Recomendación de modalidad
    # Renta vitalicia es ~4% más baja en mesada pero garantiza pago hasta muerte
    # Retiro programado puede dejar herencia si la persona vive menos que el promedio
    modalidad_recomendada = "renta_vitalicia"  # Default conservador
    
    # Observaciones
    observaciones = []
    
    if saldo_final <= 0:
        observaciones.append(
            "Sin saldo acumulado al momento de jubilación. "
            "El periodo de cotización es muy corto o los aportes son muy bajos."
        )
    
    if total_aportes > 0:
        total_rentabilidad = saldo_final - total_aportes
        rentabilidad_efectiva = (total_rentabilidad / total_aportes) * 100
        observaciones.append(
            f"Rentabilidad efectiva: {rentabilidad_efectiva:.1f}% "
            f"(generó ${total_rentabilidad:,.0f} sobre ${total_aportes:,.0f} en aportes)"
        )
    
    if total_comisiones > 0:
        observaciones.append(
            f"Comisiones AFP totales pagadas: ${total_comisiones:,.0f} "
            f"({total_comisiones/total_aportes*100:.1f}% de tus aportes)"
        )
    
    observaciones.append(
        f"Edad de jubilación asumida: {edad_jubilacion} años ({sexo}). "
        f"Fecha estimada: {fecha_jubilacion.isoformat()}"
    )
    
    anos_proyectados = anios_hasta_jubilacion + (
        (fecha_calculo - date(fecha_calculo.year, 1, 1)).days / 365.25
    )
    
    return RaisResult(
        saldo_final=saldo_final,
        total_aportes=total_aportes,
        total_rentabilidad=saldo_final - total_aportes if total_aportes > 0 else 0,
        meses_proyectados=int(anios_hasta_jubilacion * 12),
        anos_proyectados=anios_hasta_jubilacion,
        mesada_vitalicia=mesada_vitalicia,
        mesada_retiro_programado=mesada_retiro,
        modalidad_recomendada=modalidad_recomendada,
        rentabilidad_efectiva=rentabilidad_efectiva if total_aportes > 0 else 0,
        comision_total_pagada=total_comisiones,
        observaciones=observaciones,
    )


def calcular_edad_simple(fecha_nacimiento: date, referencia: date) -> int:
    """Calcula edad en años cumplidos (replica de calculator.py para evitar import circular)."""
    edad = referencia.year - fecha_nacimiento.year
    if (referencia.month, referencia.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad
