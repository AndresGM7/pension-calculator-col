"""Tests del módulo RAIS (Régimen de Ahorro Individual con Solidaridad)."""
from datetime import date

import pytest

from src.core.pension.ibc import PeriodoCotizacion
from src.core.pension.rais import (
    PORCENTAJE_COTIZACION_OBLIGATORIO,
    RENTABILIDAD_ANUAL_DEFAULT,
    RaisInput,
    calcular_meses_esperados,
    calcular_pension_rais,
    proyectar_saldo_rais,
)


def test_porcentaje_cotizacion_default_es_10_por_ciento():
    """Verifica que el porcentaje default de cotización es 10%."""
    assert PORCENTAJE_COTIZACION_OBLIGATORIO == 0.10


def test_rentabilidad_default_es_5_por_ciento():
    """Rentabilidad anual default conservadora."""
    assert RENTABILIDAD_ANUAL_DEFAULT == 0.05


def test_calcular_meses_esperados_edad_57():
    """Mujer 57 años debe esperar ~26 años (312 meses)."""
    meses = calcular_meses_esperados(57)
    assert meses == 312


def test_calcular_meses_esperados_edad_62():
    """Hombre 62 años debe esperar ~19.5 años (234 meses) segun DANE 2018-2023."""
    meses = calcular_meses_esperados(62)
    assert meses == 234


def test_calcular_meses_esperados_edad_intermedia_interpola():
    """Edad intermedia debe interpolar correctamente."""
    # 60 años está entre 57 (312) y 62 (264)
    meses = calcular_meses_esperados(60)
    assert 264 < meses < 312
    assert meses > 0


def test_calcular_meses_esperados_edad_fuera_de_rango():
    """Edades fuera de rango usan los extremos."""
    # Edad 50 está por debajo del mínimo (57)
    meses_50 = calcular_meses_esperados(50)
    assert meses_50 == 312

    # Edad 80 está por encima del máximo (70)
    meses_80 = calcular_meses_esperados(80)
    assert meses_80 == 192


def test_proyectar_saldo_rais_basico():
    """Proyección simple: 1 año cotizando con IBC fijo."""
    periodos = [
        PeriodoCotizacion(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 12, 31),
            ibc=5_000_000,  # 5M COP/mes
        ),
    ]
    rais_input = RaisInput(
        rentabilidad_anual=0.05,
        comision_afp=0.015,
    )

    # 12 meses
    saldo, aportes, comisiones = proyectar_saldo_rais(
        periodos=periodos,
        rais_input=rais_input,
        fecha_inicio=date(2025, 1, 1),
        fecha_jubilacion=date(2026, 1, 1),
    )

    # Verificaciones básicas
    assert saldo > 0
    assert aportes > 0
    assert comisiones > 0

    # El aporte bruto por mes: 5M × 10% = 500K
    # Comisión: 5M × 1.5% = 75K
    # Aporte neto: 425K/mes
    # En 12 meses: ~5.1M en aportes
    # Con capitalización 5% anual: saldo > 5.1M

    # Aproximadamente: 5.1M de aportes + ~250K de intereses = 5.35M
    assert 5_000_000 < saldo < 6_000_000, f"Saldo {saldo:,.0f} fuera de rango esperado"


def test_proyectar_saldo_rais_periodo_largo():
    """Proyección a 30 años con IBC creciente."""
    # Francisco: 30 años más de cotización con salario promedio
    periodos = []
    for year in range(2025, 2055):
        # IBC crece ~3% anual real
        ibc = 15_000_000 * (1.03 ** (year - 2025))
        periodos.append(
            PeriodoCotizacion(
                fecha_inicio=date(year, 1, 1),
                fecha_fin=date(year, 12, 31),
                ibc=ibc,
            )
        )

    rais_input = RaisInput(
        rentabilidad_anual=0.05,
        comision_afp=0.015,
    )

    saldo, aportes, comisiones = proyectar_saldo_rais(
        periodos=periodos,
        rais_input=rais_input,
        fecha_inicio=date(2025, 1, 1),
        fecha_jubilacion=date(2055, 1, 1),
    )

    # 30 años con IBC promedio ~25M
    # Aportes brutos: 25M × 10% × 12 × 30 = 900M
    # Comisiones: 25M × 1.5% × 12 × 30 = 135M
    # Aportes netos: 765M
    # Con 5% anual a 30 años, factor compuesto: 1.05^30 = 4.32
    # Saldo aproximado: 765M × 4.32 / 2 = ~1.6B (asumiendo aportes distribuidos)

    assert saldo > 1_000_000_000, f"Saldo {saldo:,.0f} muy bajo para 30 años"
    assert saldo < 5_000_000_000, f"Saldo {saldo:,.0f} muy alto"


def test_calcular_pension_rais_completo():
    """Pipeline completo: calcula pensión RAIS para un caso simple."""
    periodos = [
        PeriodoCotizacion(
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2035, 12, 31),
            ibc=8_000_000,
        ),
    ]

    # Persona de 30 años que cotiza 10 años más
    fecha_nac = date(1995, 1, 1)
    rais_input = RaisInput(
        rentabilidad_anual=0.05,
        tipo_fondo="Moderado",
        comision_afp=0.015,
    )

    result = calcular_pension_rais(
        periodos=periodos,
        rais_input=rais_input,
        fecha_nacimiento=fecha_nac,
        sexo="M",  # Se jubila a los 62
        fecha_calculo=date(2025, 1, 1),
    )

    assert result.saldo_final > 0
    assert result.mesada_vitalicia > 0
    assert result.mesada_retiro_programado > 0
    assert result.anos_proyectados > 30  # Faltan 32 años para los 62

    # Mesada vitalicia debe ser menor que retiro programado (4% admin fee)
    assert result.mesada_vitalicia < result.mesada_retiro_programado

    # Observaciones presentes
    assert len(result.observaciones) > 0


def test_pension_rais_mujer_se_jubila_antes():
    """Mujer se jubila a los 57, hombre a los 62."""
    periodos_mujer = [
        PeriodoCotizacion(date(2025, 1, 1), date(2032, 12, 31), 8_000_000),
    ]
    periodos_hombre = [
        PeriodoCotizacion(date(2025, 1, 1), date(2037, 12, 31), 8_000_000),
    ]

    rais_input = RaisInput(rentabilidad_anual=0.05)

    res_mujer = calcular_pension_rais(
        periodos=periodos_mujer,
        rais_input=rais_input,
        fecha_nacimiento=date(1995, 1, 1),
        sexo="F",
    )
    res_hombre = calcular_pension_rais(
        periodos=periodos_hombre,
        rais_input=rais_input,
        fecha_nacimiento=date(1995, 1, 1),
        sexo="M",
    )

    # Mujer cotiza menos años pero se jubila antes
    assert res_mujer.anos_proyectados < res_hombre.anos_proyectados

    # Pero la mujer espera vivir más años (más meses de retiro)
    # Por lo tanto, su mesada tiende a ser menor (mismo saldo dividido en más meses)
    # Esto NO es una regla fija - depende de los números específicos
