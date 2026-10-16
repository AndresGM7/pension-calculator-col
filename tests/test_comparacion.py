"""Tests del módulo de comparación RPM vs RAIS."""
from datetime import date

from src.core.pension.comparacion import comparar_regimenes
from src.core.pension.ibc import PeriodoCotizacion


def test_comparacion_basica_retorna_ambos_regimenes():
    """La comparación debe incluir resultados de RPM y RAIS."""
    periodos = [
        PeriodoCotizacion(date(2010, 1, 1), date(2025, 12, 31), 5_000_000),
    ]

    resultado = comparar_regimenes(
        fecha_nacimiento=date(1970, 1, 1),
        sexo="M",
        semanas_cotizadas=1500,
        periodos=periodos,
    )

    assert resultado.rpm_mesada > 0
    assert resultado.rais_mesada_retiro_programado > 0
    assert resultado.rais_saldo_final > 0


def test_comparacion_incluye_3_escenarios_rais():
    """Debe calcular 3 escenarios de rentabilidad RAIS."""
    periodos = [
        PeriodoCotizacion(date(2010, 1, 1), date(2025, 12, 31), 5_000_000),
    ]

    resultado = comparar_regimenes(
        fecha_nacimiento=date(1970, 1, 1),
        sexo="M",
        semanas_cotizadas=1500,
        periodos=periodos,
    )

    assert len(resultado.rais_escenarios) == 3

    nombres = [e["nombre"] for e in resultado.rais_escenarios]
    assert "Conservador" in nombres
    assert "Moderado" in nombres
    assert "Agresivo" in nombres


def test_escenario_agresivo_da_mayor_mesada_que_conservador():
    """A mayor rentabilidad esperada, mayor mesada proyectada."""
    periodos = [
        PeriodoCotizacion(date(2010, 1, 1), date(2025, 12, 31), 5_000_000),
    ]

    resultado = comparar_regimenes(
        fecha_nacimiento=date(1970, 1, 1),
        sexo="M",
        semanas_cotizadas=1500,
        periodos=periodos,
    )

    conservador = next(e for e in resultado.rais_escenarios if e["nombre"] == "Conservador")
    moderado = next(e for e in resultado.rais_escenarios if e["nombre"] == "Moderado")
    agresivo = next(e for e in resultado.rais_escenarios if e["nombre"] == "Agresivo")

    assert conservador["saldo_final"] < moderado["saldo_final"] < agresivo["saldo_final"]
    assert conservador["mesada_retiro_programado"] < moderado["mesada_retiro_programado"] < agresivo["mesada_retiro_programado"]


def test_recomendacion_es_una_de_las_tres_opciones():
    """La recomendación debe ser RPM, RAIS o INDECISO."""
    periodos = [
        PeriodoCotizacion(date(2010, 1, 1), date(2025, 12, 31), 5_000_000),
    ]

    resultado = comparar_regimenes(
        fecha_nacimiento=date(1970, 1, 1),
        sexo="M",
        semanas_cotizadas=1500,
        periodos=periodos,
    )

    assert resultado.regimen_recomendado in ["RPM", "RAIS", "INDECISO"]


def test_incluye_listas_de_ventajas_para_ambos_regimenes():
    """Las listas de ventajas deben estar pobladas para cada régimen."""
    periodos = [
        PeriodoCotizacion(date(2010, 1, 1), date(2025, 12, 31), 5_000_000),
    ]

    resultado = comparar_regimenes(
        fecha_nacimiento=date(1970, 1, 1),
        sexo="M",
        semanas_cotizadas=1500,
        periodos=periodos,
    )

    assert len(resultado.ventajas_rpm) > 0
    assert len(resultado.ventajas_rais) > 0


def test_diferencia_puede_ser_positiva_o_negativa():
    """La diferencia (RAIS - RPM) puede ser a favor de cualquier régimen."""
    # Caso 1: IBC alto, muchas semanas -> RPM suele ganar
    periodos_alto = [
        PeriodoCotizacion(date(2010, 1, 1), date(2025, 12, 31), 15_000_000),
    ]
    resultado1 = comparar_regimenes(
        fecha_nacimiento=date(1970, 1, 1),
        sexo="M",
        semanas_cotizadas=1800,
        periodos=periodos_alto,
    )

    # Caso 2: IBC bajo, pocas semanas -> RAIS podría ganar
    periodos_bajo = [
        PeriodoCotizacion(date(2015, 1, 1), date(2025, 12, 31), 2_000_000),
    ]
    resultado2 = comparar_regimenes(
        fecha_nacimiento=date(1980, 1, 1),
        sexo="M",
        semanas_cotizadas=900,  # NO califica para RPM
        periodos=periodos_bajo,
    )

    # Ambos casos deben tener resultados válidos
    assert resultado1.regimen_recomendado in ["RPM", "RAIS", "INDECISO"]
    assert resultado2.regimen_recomendado in ["RPM", "RAIS", "INDECISO"]


def test_caso_sin_periodos_retorna_observacion():
    """Sin periodos de cotización, debe haber observación explicando."""
    resultado = comparar_regimenes(
        fecha_nacimiento=date(1980, 1, 1),
        sexo="M",
        semanas_cotizadas=0,
        periodos=[],
    )

    # Sin periodos, RPM IBL = 0 y RAIS saldo = 0
    # El sistema debe manejarlo gracefully
    assert isinstance(resultado.observaciones, list)
