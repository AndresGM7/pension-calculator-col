"""Comparador de regímenes pensionales RPM (Colpensiones) vs RAIS (AFPs privadas).

Este módulo es el DIFERENCIADOR clave del producto. Permite al usuario ver
objetivamente cuál régimen le conviene más, sin el sesgo de ninguna entidad.

Estrategia:
- NO recomendar tajantemente. Mostrar datos, dejar que el usuario decida.
- Mostrar diferencia en pesos Y en %.
- Considerar escenarios múltiples (conservador/moderado/agresivo).
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from src.core.pension.calculator import PensionInput, PensionResult, calcular_pension
from src.core.pension.ibc import PeriodoCotizacion
from src.core.pension.rais import RaisInput, RaisResult, calcular_pension_rais


@dataclass(frozen=True)
class EscenarioRAIS:
    """Un escenario de rentabilidad para el cálculo RAIS."""
    nombre: str  # "Conservador", "Moderado", "Agresivo"
    rentabilidad_anual: float
    tipo_fondo: Literal["Conservador", "Moderado", "Mayor_Riesgo"]
    descripcion: str


# Escenarios predefinidos
ESCENARIOS_RAIS = [
    EscenarioRAIS(
        nombre="Conservador",
        rentabilidad_anual=0.035,  # 3.5% real anual
        tipo_fondo="Conservador",
        descripcion="Bonos gubernamentales, baja volatilidad. Historico ~3.5% real en Colombia.",
    ),
    EscenarioRAIS(
        nombre="Moderado",
        rentabilidad_anual=0.050,  # 5% real anual
        tipo_fondo="Moderado",
        descripcion="Mix acciones/bonos. Historico ~5% real en Colombia.",
    ),
    EscenarioRAIS(
        nombre="Agresivo",
        rentabilidad_anual=0.065,  # 6.5% real anual
        tipo_fondo="Mayor_Riesgo",
        descripcion="Mayor exposición a acciones. Historico ~6.5% real, mayor volatilidad.",
    ),
]


@dataclass(frozen=True)
class ComparacionRegimenes:
    """Resultado de comparar RPM vs RAIS."""
    
    # Datos del usuario
    fecha_nacimiento: str
    sexo: str
    semanas_cotizadas: int
    edad_actual: int
    edad_jubilacion_rpm: int
    edad_jubilacion_rais: int
    
    # Resultado RPM
    rpm_mesada: float
    rpm_ibl: float
    rpm_tasa: float
    rpm_tiene_derecho: bool
    
    # Resultado RAIS (mejor escenario = moderado)
    rais_mesada_vitalicia: float
    rais_mesada_retiro_programado: float
    rais_saldo_final: float
    rais_escenario_usado: str
    
    # Escenarios RAIS alternativos
    rais_escenarios: list[dict]  # [{"nombre": "...", "mesada": X, "saldo": Y}, ...]
    
    # Análisis comparativo
    diferencia_mensual: float  # RAIS - RPM (en mejor escenario)
    diferencia_porcentual: float  # % de diferencia
    regimen_recomendado: Literal["RPM", "RAIS", "INDECISO"]
    
    # Consideraciones adicionales
    ventajas_rpm: list[str]
    ventajas_rais: list[str]
    observaciones: list[str] = field(default_factory=list)


def _ventajas_rpm() -> list[str]:
    return [
        "Mesada fija y predecible, calculada con fórmula legal",
        "Pago garantizado por el Estado (Colpensiones)",
        "No depende de rentabilidades del mercado financiero",
        "Más alto si tenés muchas semanas cotizadas (1,800+)",
        "Indexación anual por IPC automática",
        "Pensión de sobrevivientes y auxilios funerarios incluidos",
    ]


def _ventajas_rais() -> list[str]:
    return [
        "Saldo es tuyo: si morís antes, herencia va a tu familia",
        "Rentabilidad puede superar a RPM en escenarios alcistas",
        "Portabilidad: podés cambiarte de AFP sin perder saldo",
        "Aportes voluntarios tienen beneficios tributarios",
        "Si tenés IBC alto, el saldo acumulado puede dar mejor pensión",
        "Flexibilidad: retiro programado vs renta vitalicia",
    ]


def comparar_regimenes(
    fecha_nacimiento: date,
    sexo: Literal["M", "F"],
    semanas_cotizadas: int,
    periodos: list[PeriodoCotizacion],
    regimen_rpm: Literal["LEY_100_1993", "LEY_797_2003"] = "LEY_797_2003",
    comision_afp: float = 0.015,
    usar_ipc: bool = True,
    fecha_calculo: date | None = None,
) -> ComparacionRegimenes:
    """Compara pensión esperada bajo RPM vs RAIS.
    
    Args:
        fecha_nacimiento: Fecha de nacimiento
        sexo: M o F
        semanas_cotizadas: Semanas cotizadas a la fecha
        periodos: Historia laboral con IBCs
        regimen_rpm: Ley aplicable para RPM
        comision_afp: Comisión AFP (default 1.5%)
        usar_ipc: Si indexar IBCs al IPC
        fecha_calculo: Fecha de referencia (default: hoy)
    
    Returns:
        ComparacionRegimenes con análisis completo
    """
    if fecha_calculo is None:
        fecha_calculo = date.today()
    
    # Calcular RPM
    rpm_input = PensionInput(
        fecha_nacimiento=fecha_nacimiento,
        sexo=sexo,
        semanas_cotizadas=semanas_cotizadas,
        periodos=periodos,
        regimen=regimen_rpm,
        usar_ipc=usar_ipc,
    )
    rpm_result = calcular_pension(rpm_input)
    
    # Calcular RAIS en 3 escenarios
    rais_resultados = []
    for escenario in ESCENARIOS_RAIS:
        rais_input = RaisInput(
            rentabilidad_anual=escenario.rentabilidad_anual,
            tipo_fondo=escenario.tipo_fondo,
            comision_afp=comision_afp,
            modalidad="retiro_programado",  # Para comparar apples-to-apples
        )
        rais_result = calcular_pension_rais(
            periodos=periodos,
            rais_input=rais_input,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            fecha_calculo=fecha_calculo,
        )
        rais_resultados.append({
            "nombre": escenario.nombre,
            "rentabilidad_anual": escenario.rentabilidad_anual,
            "tipo_fondo": escenario.tipo_fondo,
            "descripcion": escenario.descripcion,
            "saldo_final": rais_result.saldo_final,
            "mesada_vitalicia": rais_result.mesada_vitalicia,
            "mesada_retiro_programado": rais_result.mesada_retiro_programado,
        })
    
    # Usar escenario moderado como referencia principal
    rais_moderado = rais_resultados[1]  # Escenario Moderado
    rais_mesada = rais_moderado["mesada_retiro_programado"]
    
    # Calcular diferencia
    diferencia = rais_mesada - rpm_result.mesada_pensional
    if rpm_result.mesada_pensional > 0:
        diferencia_pct = (diferencia / rpm_result.mesada_pensional) * 100
    else:
        diferencia_pct = 0
    
    # Recomendacion con proteccion contra datos invalidos
    if not rpm_result.tiene_derecho:
        # Si no tiene derecho a RPM, no puede elegir RPM como opcion.
        # La comparacion debe inclinarse hacia RAIS o quedar indeciso.
        recomendado = "RAIS"  # RAIS no requiere minimo de semanas
    elif rpm_result.mesada_pensional == 0:
        # RPM da $0 (sin periodos cotizados), recomendar RAIS
        recomendado = "RAIS"
    elif abs(diferencia_pct) < 5:
        recomendado = "INDECISO"
    elif diferencia > 0:
        recomendado = "RAIS"
    else:
        recomendado = "RPM"
    
    # Edad de jubilación
    edad_jubilacion_rpm = 62 if sexo == "M" else 57
    edad_actual = rpm_result.edad_actual
    
    # Observaciones personalizadas
    observaciones = []
    
    if rpm_result.tasa_reemplazo >= 0.65 and sexo == "F":
        observaciones.append(
            "Como mujer, tu tasa de reemplazo base es 65% (Ley 797/2003). "
            "RAIS podría ser más competitivo si elegís fondo agresivo."
        )
    
    if semanas_cotizadas < 1300:
        observaciones.append(
            f"Con {semanas_cotizadas} semanas NO alcanzas el minimo para RPM (1,300). "
            "En RAIS no hay minimo de semanas: tu saldo se acumula de todas formas. "
            f"Te faltan {1300 - semanas_cotizadas} semanas para calificar a RPM."
        )
    if not rpm_result.tiene_derecho:
        observaciones.append(
            "IMPORTANTE: No calificas para RPM (no cumples semanas o edad minima). "
            "Esta comparacion es informativa; tu unica opcion real es RAIS o seguir cotizando."
        )
    
    if rais_moderado["saldo_final"] > rpm_result.ibl_calculado * 240 * 1.5:
        observaciones.append(
            "Tu saldo proyectado RAIS es alto. Esto puede indicar que RAIS te conviene, "
            "especialmente si tenés herederos (el saldo no usado va a tu familia)."
        )
    
    return ComparacionRegimenes(
        fecha_nacimiento=fecha_nacimiento.isoformat(),
        sexo=sexo,
        semanas_cotizadas=semanas_cotizadas,
        edad_actual=edad_actual,
        edad_jubilacion_rpm=edad_jubilacion_rpm,
        edad_jubilacion_rais=edad_jubilacion_rpm,  # Misma edad
        rpm_mesada=rpm_result.mesada_pensional,
        rpm_ibl=rpm_result.ibl_calculado,
        rpm_tasa=rpm_result.tasa_reemplazo,
        rpm_tiene_derecho=rpm_result.tiene_derecho,
        rais_mesada_vitalicia=rais_moderado["mesada_vitalicia"],
        rais_mesada_retiro_programado=rais_moderado["mesada_retiro_programado"],
        rais_saldo_final=rais_moderado["saldo_final"],
        rais_escenario_usado="Moderado",
        rais_escenarios=rais_resultados,
        diferencia_mensual=diferencia,
        diferencia_porcentual=diferencia_pct,
        regimen_recomendado=recomendado,
        ventajas_rpm=_ventajas_rpm(),
        ventajas_rais=_ventajas_rais(),
        observaciones=observaciones,
    )
