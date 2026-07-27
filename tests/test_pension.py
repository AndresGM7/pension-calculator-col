"""Tests para el motor de cálculo pensional."""
from datetime import date

from src.core.pension.calculator import PensionInput, calcular_pension
from src.core.pension.ibc import PeriodoCotizacion


def _make_periodos_minimos():
    """Crea unos periodos mínimos para los tests."""
    return [
        PeriodoCotizacion(date(2000, 1, 1), date(2010, 1, 1), 2_000_000),
    ]


def test_tiene_derecho_con_semanas_minimas():
    """Con 1,300 semanas y edad suficiente, debe tener derecho."""
    input_data = PensionInput(
        fecha_nacimiento=date(1960, 1, 1),  # 66 años
        sexo="M",
        semanas_cotizadas=1300,
        periodos=_make_periodos_minimos(),
    )
    result = calcular_pension(input_data)
    assert result.tiene_derecho is True
    assert result.tasa_reemplazo == 0.65  # 1,300 semanas → 65%


def test_no_tiene_derecho_por_edad():
    """Joven con suficientes semanas no califica."""
    input_data = PensionInput(
        fecha_nacimiento=date(1990, 1, 1),  # 36 años
        sexo="M",
        semanas_cotizadas=1500,
        periodos=_make_periodos_minimos(),
    )
    result = calcular_pension(input_data)
    assert result.tiene_derecho is False
    assert any("Edad" in obs for obs in result.observaciones)


def test_no_tiene_derecho_por_semanas():
    """Edad suficiente pero pocas semanas no califica."""
    input_data = PensionInput(
        fecha_nacimiento=date(1960, 1, 1),
        sexo="M",
        semanas_cotizadas=800,
        periodos=_make_periodos_minimos(),
    )
    result = calcular_pension(input_data)
    assert result.tiene_derecho is False
    assert any("Semanas" in obs for obs in result.observaciones)


def test_tasa_reemplazo_por_tramos():
    """Verifica tasa de reemplazo Ley 797/2003 vigente.

    Con IBL bajo (1 SMLMV), la tasa es ~65% (maximo).
    Con IBL alto (10+ SMLMV), la tasa es ~55% (minimo).
    Suma 1.5% cada 50 semanas. Maximo 80%.
    """
    # Mismo IBL, mas semanas = mas tasa
    assert _calcular_tasa(1300) < _calcular_tasa(1500)
    assert _calcular_tasa(1500) < _calcular_tasa(1700)
    # Tope maximo
    assert _calcular_tasa(2000) <= 0.80


def _calcular_tasa(semanas, ibl_val=1_300_000):
    """Helper. Calcula tasa para un numero dado de semanas y un IBL opcional."""
    periodos = [PeriodoCotizacion(date(2020, 1, 1), date(2025, 1, 1), ibl_val)]
    input_data = PensionInput(
        fecha_nacimiento=date(1960, 1, 1),
        sexo="M",
        semanas_cotizadas=semanas,
        periodos=periodos,
    )
    result = calcular_pension(input_data)
    return result.tasa_reemplazo


def test_ley_100_vs_ley_797_difieren():
    """Ley 797/2003 y Ley 100/1993 deben diferenciarse."""
    periodos = [PeriodoCotizacion(date(2020, 1, 1), date(2025, 1, 1), 2_000_000)]

    # Con 1,500 semanas (califica para ambos regimenes)
    base = PensionInput(
        fecha_nacimiento=date(1960, 1, 1),
        sexo="M",
        semanas_cotizadas=1500,
        periodos=periodos,
        regimen="LEY_797_2003",
    )
    other = PensionInput(
        fecha_nacimiento=date(1960, 1, 1),
        sexo="M",
        semanas_cotizadas=1500,
        periodos=periodos,
        regimen="LEY_100_1993",
    )
    r1 = calcular_pension(base)
    r2 = calcular_pension(other)
    # Ambos regimenes producen tasas diferentes
    assert r1.tasa_reemplazo != r2.tasa_reemplazo
    # Ninguno debe ser cero
    assert r1.tasa_reemplazo > 0
    assert r2.tasa_reemplazo > 0


def test_mujeres_jubilan_mas_temprano():
    """Mujeres a los 57, hombres a los 62."""
    periodos = _make_periodos_minimos()

    hombre = PensionInput(
        fecha_nacimiento=date(1967, 1, 1),  # 59 años
        sexo="M",
        semanas_cotizadas=1300,
        periodos=periodos,
    )
    mujer = PensionInput(
        fecha_nacimiento=date(1967, 1, 1),
        sexo="F",
        semanas_cotizadas=1300,
        periodos=periodos,
    )
    r_h = calcular_pension(hombre)
    r_m = calcular_pension(mujer)
    assert r_m.tiene_derecho is True   # 59 >= 57
    assert r_h.tiene_derecho is False  # 59 < 62
