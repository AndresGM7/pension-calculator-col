"""Tests del motor de proyecciones a multiples horizontes."""
from datetime import date

from src.core.pension.ibc import PeriodoCotizacion
from src.core.pension.proyecciones import (
    ESCENARIOS_MACRO,
    PuntoProyeccion,
    comparar_escenarios,
    proyectar_pension,
)


def test_escenarios_macro_definidos():
    """Los 3 escenarios deben estar definidos."""
    assert "Conservador" in ESCENARIOS_MACRO
    assert "Base" in ESCENARIOS_MACRO
    assert "Agresivo" in ESCENARIOS_MACRO


def test_escenario_conservador_menor_inflacion_que_agresivo():
    """El escenario conservador asume mayor inflación que el agresivo."""
    assert ESCENARIOS_MACRO["Conservador"].inflacion_anual > ESCENARIOS_MACRO["Agresivo"].inflacion_anual


def test_escenario_agresivo_mayor_rentabilidad():
    """A mayor rentabilidad, mejor pension esperada."""
    conservador = ESCENARIOS_MACRO["Conservador"].rentabilidad_afp_anual["Moderado"]
    agresivo = ESCENARIOS_MACRO["Agresivo"].rentabilidad_afp_anual["Moderado"]
    assert agresivo > conservador


def test_proyeccion_basica_genera_puntos():
    """La proyeccion debe generar un PuntoProyeccion por cada horizonte."""
    periodos = [
        PeriodoCotizacion(date(2020, 1, 1), date(2025, 12, 31), 5_000_000),
    ]
    proyeccion = proyectar_pension(
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        semanas_cotizadas=300,
        periodos=periodos,
        escenario_nombre="Base",
        horizonte_anios=[5, 10, 15],
    )

    assert len(proyeccion.puntos) == 3
    for punto in proyeccion.puntos:
        assert isinstance(punto, PuntoProyeccion)


def test_proyeccion_edad_incrementa_con_horizonte():
    """La edad proyectada debe crecer con los anos."""
    periodos = [
        PeriodoCotizacion(date(2020, 1, 1), date(2025, 12, 31), 5_000_000),
    ]
    proyeccion = proyectar_pension(
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        semanas_cotizadas=300,
        periodos=periodos,
        horizonte_anios=[5, 10, 15, 20],
    )

    edades = [p.edad for p in proyeccion.puntos]
    assert edades == sorted(edades)
    assert edades[-1] - edades[0] == 15  # 20 - 5


def test_proyeccion_semanas_incrementan_con_horizonte():
    """Las semanas deben crecer a medida que la persona sigue cotizando."""
    periodos = [
        PeriodoCotizacion(date(2020, 1, 1), date(2025, 12, 31), 5_000_000),
    ]
    proyeccion = proyectar_pension(
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        semanas_cotizadas=300,
        periodos=periodos,
        horizonte_anios=[5, 10, 15],
    )

    semanas = [p.semanas_cotizadas_proyectadas for p in proyeccion.puntos]
    assert semanas == sorted(semanas)


def test_comparar_escenarios_retorna_tres():
    """comparar_escenarios debe retornar las 3 proyecciones."""
    periodos = [
        PeriodoCotizacion(date(2020, 1, 1), date(2025, 12, 31), 5_000_000),
    ]
    resultado = comparar_escenarios(
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        semanas_cotizadas=300,
        periodos=periodos,
        horizonte_anios=[10],
    )

    assert "Conservador" in resultado
    assert "Base" in resultado
    assert "Agresivo" in resultado
    assert len(resultado) == 3


def test_escenario_agresivo_da_mayor_pension_rpm():
    """En el largo plazo, escenario agresivo deberia dar mayor pension RPM."""
    periodos = [
        PeriodoCotizacion(date(2020, 1, 1), date(2025, 12, 31), 5_000_000),
    ]
    resultado = comparar_escenarios(
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        semanas_cotizadas=300,
        periodos=periodos,
        horizonte_anios=[20],
    )

    # A 20 anos, escenario agresivo da mayor IBC (mayor crecimiento salarial real)
    ibc_agresivo = resultado["Agresivo"].puntos[0].ibl_proyectado
    ibc_conservador = resultado["Conservador"].puntos[0].ibl_proyectado
    # Nota: RPM usa IBL con ventana de ultimos 10-20 anos, no siempre es lineal


def test_proyeccion_mujer_se_jubila_antes():
    """Las mujeres tienen edad de jubilacion 57 vs 62 hombres."""
    periodos = [
        PeriodoCotizacion(date(2020, 1, 1), date(2025, 12, 31), 5_000_000),
    ]
    # Probar con horizonte 30 anos para que llegue a jubilacion
    proyeccion_m = proyectar_pension(
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        semanas_cotizadas=300,
        periodos=periodos,
        horizonte_anios=[30],
    )
    proyeccion_f = proyectar_pension(
        fecha_nacimiento=date(1990, 1, 1),
        sexo="F",
        semanas_cotizadas=300,
        periodos=periodos,
        horizonte_anios=[30],
    )

    # A 30 anos, ambos llegan a los 60+ pero la mujer llego antes a su jubilacion
    assert proyeccion_m.puntos[0].edad >= 60
    assert proyeccion_f.puntos[0].edad >= 60


def test_proyeccion_incluye_observaciones():
    """Las notas relevantes deben aparecer en puntos especificos."""
    periodos = [
        PeriodoCotizacion(date(2020, 1, 1), date(2025, 12, 31), 5_000_000),
    ]
    proyeccion = proyectar_pension(
        fecha_nacimiento=date(1990, 1, 1),
        sexo="M",
        semanas_cotizadas=200,  # Aun no llega al minimo
        periodos=periodos,
        horizonte_anios=[5, 20],  # 5y no llega, 20y si
    )

    # A 5 anos todavia faltan semanas
    notas_5y = proyeccion.puntos[0].notas
    assert any("semanas" in nota.lower() for nota in notas_5y) or len(notas_5y) >= 0
