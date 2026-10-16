"""Motor de proyecciones a 5-10-15-20 años bajo multiples escenarios.

Para una persona en cualquier momento de su vida laboral, este modulo proyecta:
- Cuanto habra cotizado a 5, 10, 15, 20 años
- Cuanta pension esperaria bajo RPM (IBL proyectado con IBC futuro estimado)
- Cuanta pension esperaria bajo RAIS (saldo acumulado proyectado)
- En 3 escenarios: Conservador, Base, Agresivo

Los 3 escenarios se diferencian en:
- Inflacion esperada (impacta IBL futuro en RPM)
- Rentabilidad esperada de AFPs (impacta saldo en RAIS)
- Crecimiento salarial real (impacta IBC futuro)
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from src.core.pension.calculator import PensionInput, calcular_pension
from src.core.pension.ibc import PeriodoCotizacion
from src.core.pension.rais import RaisInput, calcular_pension_rais


@dataclass(frozen=True)
class EscenarioMacro:
    """Parametros macroeconomicos de un escenario."""
    nombre: str  # "Conservador", "Base", "Agresivo"
    descripcion: str

    inflacion_anual: float  # % anual esperada
    crecimiento_salarial_real: float  # % anual real (sobre inflacion)
    rentabilidad_afp_anual: dict[str, float]  # {"Conservador": 0.04, "Moderado": 0.05, ...}


# Escenarios predefinidos (basados en historico Colombia 2000-2025)
ESCENARIOS_MACRO = {
    "Conservador": EscenarioMacro(
        nombre="Conservador",
        descripcion="Inflacion alta (8% anual), crecimiento salarial real bajo (0.5%), rentabilidades bajas (3-4% real)",
        inflacion_anual=0.08,
        crecimiento_salarial_real=0.005,
        rentabilidad_afp_anual={
            "Conservador": 0.025,  # 2.5% real
            "Moderado": 0.035,     # 3.5% real
            "Mayor_Riesgo": 0.045, # 4.5% real
        },
    ),
    "Base": EscenarioMacro(
        nombre="Base",
        descripcion="Inflacion moderada (5% anual), crecimiento salarial real estable (1.5%), rentabilidades moderadas (4-5% real)",
        inflacion_anual=0.05,
        crecimiento_salarial_real=0.015,
        rentabilidad_afp_anual={
            "Conservador": 0.035,
            "Moderado": 0.05,
            "Mayor_Riesgo": 0.065,
        },
    ),
    "Agresivo": EscenarioMacro(
        nombre="Agresivo",
        descripcion="Inflacion controlada (3% anual), crecimiento salarial real alto (2.5%), rentabilidades altas (5-7% real)",
        inflacion_anual=0.03,
        crecimiento_salarial_real=0.025,
        rentabilidad_afp_anual={
            "Conservador": 0.045,
            "Moderado": 0.065,
            "Mayor_Riesgo": 0.085,
        },
    ),
}


@dataclass(frozen=True)
class PuntoProyeccion:
    """Estado proyectado en un momento del tiempo."""
    anios_desde_hoy: int
    fecha: str  # ISO date

    # Persona en ese momento
    edad: int
    semanas_cotizadas_proyectadas: int

    # RPM (Colpensiones)
    ibl_proyectado: float
    tasa_reemplazo_proyectada: float
    mesada_rpm_proyectada: float

    # RAIS (AFPs privadas)
    saldo_rais_proyectado: float
    mesada_rais_vitalicia: float
    mesada_rais_retiro_programado: float

    # Observaciones
    notas: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProyeccionCompleta:
    """Proyeccion completa a multiples horizontes."""
    fecha_calculo: str
    fecha_nacimiento: str
    sexo: str
    edad_actual: int
    semanas_cotizadas_actuales: int
    horizonte_anios: list[int]

    escenario: str  # "Conservador", "Base", "Agresivo"
    descripcion_escenario: str

    # Resultados por horizonte temporal
    puntos: list[PuntoProyeccion]


def _proyectar_periodos(
    periodos: list[PeriodoCotizacion],
    fecha_inicio: date,
    fecha_fin: date,
    ibc_crecimiento_anual: float,
) -> list[PeriodoCotizacion]:
    """Proyecta periodos futuros asumiendo que la persona sigue cotizando
    con el mismo patron temporal pero con IBC que crece anualmente.

    Args:
        periodos: Periodos historicos (para inferir patron temporal)
        fecha_inicio: Fecha actual
        fecha_fin: Fecha de proyeccion (ej. 5 años despues)
        ibc_crecimiento_anual: % de crecimiento anual del IBC (real o nominal)

    Returns:
        Lista extendida de periodos con IBCs proyectados
    """
    if not periodos:
        # Si no hay periodos historicos, asumimos IBC constante
        return []

    # Tomar el IBC promedio de los ultimos 3 anos como base
    ultimos_3y = [p for p in periodos if p.fecha_inicio >= date(
        fecha_inicio.year - 3, fecha_inicio.month, fecha_inicio.day
    )]
    if ultimos_3y:
        ibc_base = sum(p.ibc for p in ultimos_3y) / len(ultimos_3y)
    else:
        ibc_base = sum(p.ibc for p in periodos[-3:]) / min(3, len(periodos))

    # Calcular cuantos meses de cotizacion por ano (de los periodos historicos)
    if len(periodos) > 1:
        dias_totales = sum(
            (p.fecha_fin - p.fecha_inicio).days for p in periodos
        )
        anios_totales = (periodos[-1].fecha_fin - periodos[0].fecha_inicio).days / 365.25
        meses_por_anio = (dias_totales / 30.44) / max(anios_totales, 1)
        meses_por_anio = min(meses_por_anio, 12)  # max 12 meses/anio
    else:
        meses_por_anio = 12

    # Proyectar anio por anio
    periodos_proyectados = list(periodos)  # copiar historicos
    for year_offset in range(1, (fecha_fin.year - fecha_inicio.year) + 1):
        anio_objetivo = fecha_inicio.year + year_offset
        ibc_proyectado = ibc_base * ((1 + ibc_crecimiento_anual) ** year_offset)

        # Distribuir meses proporcionalmente a lo largo del anio
        if meses_por_anio >= 12:
            inicio = date(anio_objetivo, 1, 1)
            fin = date(anio_objetivo, 12, 31)
            periodos_proyectados.append(PeriodoCotizacion(inicio, fin, ibc_proyectado))
        else:
            # Distribuir meses_por_anio a lo largo del anio
            meses_distribuidos = max(1, int(meses_por_anio))
            dias_por_periodo = 365 // meses_distribuidos
            for mes_idx in range(meses_distribuidos):
                mes_inicio = 1 + (mes_idx * dias_por_periodo // 30)
                if mes_inicio > 12:
                    break
                mes_fin = min(12, mes_inicio + 1)
                inicio = date(anio_objetivo, mes_inicio, 1)
                fin = date(anio_objetivo, mes_fin, 28)
                periodos_proyectados.append(
                    PeriodoCotizacion(inicio, fin, ibc_proyectado)
                )

    return periodos_proyectados


def calcular_edad_simple(fecha_nacimiento: date, referencia: date) -> int:
    """Calcula edad en años cumplidos."""
    edad = referencia.year - fecha_nacimiento.year
    if (referencia.month, referencia.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def proyectar_pension(
    fecha_nacimiento: date,
    sexo: Literal["M", "F"],
    semanas_cotizadas: int,
    periodos: list[PeriodoCotizacion],
    escenario_nombre: Literal["Conservador", "Base", "Agresivo"] = "Base",
    horizonte_anios: list[int] = None,
    regimen_rpm: Literal["LEY_100_1993", "LEY_797_2003"] = "LEY_797_2003",
    tipo_fondo_rais: Literal["Conservador", "Moderado", "Mayor_Riesgo"] = "Moderado",
    fecha_calculo: date | None = None,
) -> ProyeccionCompleta:
    """Proyecta pension a multiples horizontes bajo un escenario macro.

    Args:
        fecha_nacimiento: Fecha de nacimiento
        sexo: M o F
        semanas_cotizadas: Semanas actuales
        periodos: Historia laboral hasta hoy
        escenario_nombre: Escenario macro a usar
        horizonte_anios: Lista de horizontes (default: [5, 10, 15, 20])
        regimen_rpm: Ley aplicable para RPM
        tipo_fondo_rais: Tipo de fondo RAIS a proyectar
        fecha_calculo: Fecha de referencia (default: hoy)

    Returns:
        ProyeccionCompleta con todos los puntos
    """
    if fecha_calculo is None:
        fecha_calculo = date.today()

    if horizonte_anios is None:
        horizonte_anios = [5, 10, 15, 20]

    escenario = ESCENARIOS_MACRO[escenario_nombre]

    # Crecimiento nominal del IBC (incluye inflacion)
    crecimiento_nominal = escenario.crecimiento_salarial_real + escenario.inflacion_anual

    edad_actual = calcular_edad_simple(fecha_nacimiento, fecha_calculo)
    edad_jubilacion_referencia = 62 if sexo == "M" else 57

    # Si la persona ya esta en edad de jubilacion, las proyecciones
    # a 5/10/15/20 anos no aplican (ya no sigue cotizando).
    # En ese caso, devolvemos el calculo actual con observaciones claras.
    ya_jubilado = edad_actual >= edad_jubilacion_referencia

    puntos = []
    for horizonte in horizonte_anios:
        if ya_jubilado:
            # No proyectar mas alla de la fecha actual - calcular pension actual
            rpm_input_actual = PensionInput(
                fecha_nacimiento=fecha_nacimiento,
                sexo=sexo,
                semanas_cotizadas=semanas_cotizadas,
                periodos=periodos,
                regimen=regimen_rpm,
                usar_ipc=True,
                fecha_referencia_ibl=fecha_calculo,
            )
            rpm_result_actual = calcular_pension(rpm_input_actual)
            rais_input_actual = RaisInput(
                saldo_inicial=0,
                fecha_saldo_inicial=fecha_calculo,
                rentabilidad_anual=escenario.rentabilidad_afp_anual[tipo_fondo_rais],
                tipo_fondo=tipo_fondo_rais,
                comision_afp=0.015,
                modalidad="retiro_programado",
            )
            rais_result_actual = calcular_pension_rais(
                periodos=[],
                rais_input=rais_input_actual,
                fecha_nacimiento=fecha_nacimiento,
                sexo=sexo,
                fecha_calculo=fecha_calculo,
            )
            puntos.append(
                PuntoProyeccion(
                    anios_desde_hoy=horizonte,
                    fecha=fecha_calculo.isoformat(),
                    edad=edad_actual,
                    semanas_cotizadas_proyectadas=semanas_cotizadas,
                    ibl_proyectado=rpm_result_actual.ibl_calculado,
                    tasa_reemplazo_proyectada=rpm_result_actual.tasa_reemplazo,
                    mesada_rpm_proyectada=rpm_result_actual.mesada_pensional,
                    saldo_rais_proyectado=0.0,
                    mesada_rais_vitalicia=0.0,
                    mesada_rais_retiro_programado=0.0,
                    notas=[
                        f"Ya tienes {edad_actual} años (edad jubilacion = {edad_jubilacion_referencia}).",
                        "Las proyecciones a futuro no aplican porque ya no cotizas.",
                        "Los valores mostrados son tu pension estimada HOY.",
                    ],
                )
            )
            continue
        fecha_proyeccion = date(
            fecha_calculo.year + horizonte,
            fecha_calculo.month,
            fecha_calculo.day,
        )
        edad_proyectada = calcular_edad_simple(fecha_nacimiento, fecha_proyeccion)

        # Proyectar semanas (asumimos que sigue cotizando igual que historicamente)
        # ~50 semanas por anio cotizando
        if len(periodos) > 1:
            semanas_por_anio_historico = 0
            for p in periodos:
                dias = (p.fecha_fin - p.fecha_inicio).days
                semanas_por_anio_historico += dias / 7
            anios_totales = (periodos[-1].fecha_fin - periodos[0].fecha_inicio).days / 365.25
            semanas_por_anio = semanas_por_anio_historico / max(anios_totales, 1)
        else:
            semanas_por_anio = 50  # default razonable

        semanas_proyectadas = semanas_cotizadas + int(semanas_por_anio * horizonte)

        # Proyectar periodos con IBCs crecientes
        periodos_proyectados = _proyectar_periodos(
            periodos=periodos,
            fecha_inicio=fecha_calculo,
            fecha_fin=fecha_proyeccion,
            ibc_crecimiento_anual=crecimiento_nominal,
        )

        # Calcular RPM en el horizonte
        rpm_input = PensionInput(
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            semanas_cotizadas=semanas_proyectadas,
            periodos=periodos_proyectados,
            regimen=regimen_rpm,
            usar_ipc=True,
            fecha_referencia_ibl=fecha_proyeccion,
        )
        rpm_result = calcular_pension(rpm_input)

        # Calcular RAIS en el horizonte
        # Para proyeccion, asumimos que el usuario ya esta en RAIS desde ahora
        # El saldo inicial crece desde 0 (asumimos no hay saldo previo significativo)
        rais_input = RaisInput(
            saldo_inicial=0,
            fecha_saldo_inicial=fecha_calculo,
            rentabilidad_anual=escenario.rentabilidad_afp_anual[tipo_fondo_rais],
            tipo_fondo=tipo_fondo_rais,
            comision_afp=0.015,
            modalidad="retiro_programado",
        )
        # Solo usar periodos FUTUROS desde hoy para proyectar
        periodos_futuros = [
            p for p in periodos_proyectados
            if p.fecha_inicio >= fecha_calculo
        ]

        rais_result = calcular_pension_rais(
            periodos=periodos_futuros,
            rais_input=rais_input,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            fecha_calculo=fecha_calculo,
        )

        # Calcular edad de jubilacion en horizonte
        if sexo == "M":
            edad_jubilacion = 62
        else:
            edad_jubilacion = 57

        notas = []
        if rpm_result.tasa_reemplazo >= 0.65:
            notas.append("Tasa de reemplazo maxima o cerca del tope 80%")
        if not rpm_result.tiene_derecho:
            semanas_faltantes = max(0, 1300 - semanas_proyectadas)
            if semanas_faltantes > 0:
                notas.append(f"Aun faltan {semanas_faltantes} semanas para minimo RPM")

        puntos.append(
            PuntoProyeccion(
                anios_desde_hoy=horizonte,
                fecha=fecha_proyeccion.isoformat(),
                edad=edad_proyectada,
                semanas_cotizadas_proyectadas=semanas_proyectadas,
                ibl_proyectado=rpm_result.ibl_calculado,
                tasa_reemplazo_proyectada=rpm_result.tasa_reemplazo,
                mesada_rpm_proyectada=rpm_result.mesada_pensional,
                saldo_rais_proyectado=rais_result.saldo_final,
                mesada_rais_vitalicia=rais_result.mesada_vitalicia,
                mesada_rais_retiro_programado=rais_result.mesada_retiro_programado,
                notas=notas,
            )
        )

    return ProyeccionCompleta(
        fecha_calculo=fecha_calculo.isoformat(),
        fecha_nacimiento=fecha_nacimiento.isoformat(),
        sexo=sexo,
        edad_actual=edad_actual,
        semanas_cotizadas_actuales=semanas_cotizadas,
        horizonte_anios=horizonte_anios,
        escenario=escenario.nombre,
        descripcion_escenario=escenario.descripcion,
        puntos=puntos,
    )


def comparar_escenarios(
    fecha_nacimiento: date,
    sexo: Literal["M", "F"],
    semanas_cotizadas: int,
    periodos: list[PeriodoCotizacion],
    horizonte_anios: list[int] = None,
    regimen_rpm: Literal["LEY_100_1993", "LEY_797_2003"] = "LEY_797_2003",
    tipo_fondo_rais: Literal["Conservador", "Moderado", "Mayor_Riesgo"] = "Moderado",
    fecha_calculo: date | None = None,
) -> dict[str, ProyeccionCompleta]:
    """Proyecta la pension bajo los 3 escenarios (Conservador, Base, Agresivo).

    Returns:
        Dict {nombre_escenario: ProyeccionCompleta}
    """
    return {
        nombre: proyectar_pension(
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            semanas_cotizadas=semanas_cotizadas,
            periodos=periodos,
            escenario_nombre=nombre,
            horizonte_anios=horizonte_anios,
            regimen_rpm=regimen_rpm,
            tipo_fondo_rais=tipo_fondo_rais,
            fecha_calculo=fecha_calculo,
        )
        for nombre in ["Conservador", "Base", "Agresivo"]
    }
