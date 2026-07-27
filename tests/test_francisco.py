"""Test con la historia laboral real de Francisco Luis Giraldo Gutierrez.

DATOS VERIFICADOS DEL PDF DE COLPENSIONES:
    - CC: 71647133
    - Fecha nacimiento: 06/12/1963 (62 años en 2026)
    - Cotizante activo desde 28/08/1984 (empleador actual: Instituto Tecnológico Metropolitano)
    - Salarios:
        - 1984-1985: ~$14.610 COP/mes
        - 1995-2000: $118.933 a $389.200 COP/mes
        - 2024-2025: $14.414.558 a $19.829.529 COP/mes (¡40 años después!)
"""
from datetime import date

from src.core.pension.calculator import PensionInput, calcular_pension
from src.core.pension.ibc import PeriodoCotizacion


def test_francisco_historico_completo():
    """Francisco — usando periodos de los 40 años de cotización.

    Para un cálculo REAL necesitaríamos parsear los ~80+ periodos
    del PDF. Ac usamos una muestra representativa.
    """
    periodos = [
        # Inicio (1984-1985)
        PeriodoCotizacion(date(1984, 8, 28), date(1985, 1, 16), 14_610),
        # Finales de los 90s
        PeriodoCotizacion(date(1996, 1, 1), date(1996, 5, 31), 142_125),
        PeriodoCotizacion(date(1997, 1, 1), date(1997, 8, 31), 164_000),
        PeriodoCotizacion(date(1998, 5, 1), date(1998, 11, 30), 209_000),
        PeriodoCotizacion(date(1999, 3, 1), date(1999, 12, 31), 264_000),
        # 2000s (último periodo con salario bajo del PDF)
        PeriodoCotizacion(date(2000, 1, 1), date(2000, 4, 30), 320_000),
        PeriodoCotizacion(date(2000, 5, 1), date(2000, 7, 31), 389_200),
        # 2024-2025 (último empleador: Instituto Tecnológico)
        PeriodoCotizacion(date(2025, 1, 1), date(2025, 3, 31), 15_348_653),
        PeriodoCotizacion(date(2025, 4, 1), date(2025, 6, 30), 18_502_790),
        PeriodoCotizacion(date(2025, 7, 1), date(2025, 9, 30), 19_829_529),
        PeriodoCotizacion(date(2025, 10, 1), date(2025, 12, 31), 16_783_393),
    ]

    input_data = PensionInput(
        fecha_nacimiento=date(1963, 12, 6),
        sexo="M",
        semanas_cotizadas=1289,  # REAL Colpensiones
        periodos=periodos,
    )

    result = calcular_pension(input_data)

    print("\n=== Pensión estimada de Francisco (caso real) ===")
    print(f"Tiene derecho: {result.tiene_derecho}")
    print(f"Edad actual: {result.edad_actual} años")
    print(f"Semanas cotizadas: {result.semanas_cotizadas}")
    print(f"Ventana IBL: {result.ventana_utilizada}")
    print(f"IBL calculado: ${result.ibl_calculado:,.2f} COP")
    print(f"Tasa reemplazo: {result.tasa_reemplazo*100:.1f}%")
    print(f"MESADA ESTIMADA: ${result.mesada_pensional:,.2f} COP/mes")
    print(f"= ${result.mesada_pensional*12:,.2f} COP/año")
    print("="*50)

    # 1,289 < 1,300: NO califica. El motor calcula igual con tasa proyectada.
    assert result.tiene_derecho is False
    assert result.mesada_pensional > 0, f"No tiene derecho: {result.observaciones}"


def test_francisco_solo_periodos_recientes():
    """Si solo usamos los periodos recientes (ventana 10 años).

    Esto es lo que APLICARÍA con Ley 797/2003 para 1,300-1,800 semanas.
    """
    periodos = [
        PeriodoCotizacion(date(2025, 1, 1), date(2025, 3, 31), 15_348_653),
        PeriodoCotizacion(date(2025, 4, 1), date(2025, 6, 30), 18_502_790),
        PeriodoCotizacion(date(2025, 7, 1), date(2025, 9, 30), 19_829_529),
        PeriodoCotizacion(date(2025, 10, 1), date(2025, 12, 31), 16_783_393),
    ]

    input_data = PensionInput(
        fecha_nacimiento=date(1963, 12, 6),
        sexo="M",
        semanas_cotizadas=1289,
        periodos=periodos,
    )

    result = calcular_pension(input_data)

    print("\n=== IBL con SOLO periodos 2025 ===")
    print(f"IBL: ${result.ibl_calculado:,.2f} COP/mes")
    print(f"Ventana: {result.ventana_utilizada}")
    print(f"NOTA: este sería el cálculo si SOLO usáramos 2025,")
    print(f"  pero la ventana son los ÚLTIMOS 10 años, no solo 2025.")
    print("="*50)

    # 1,289 < 1,300: NO califica. El motor calcula igual con tasa proyectada.
    assert result.tiene_derecho is False
    assert result.mesada_pensional > 0


def test_tasa_cotizacion_evoluciona():
    """Verifica que la tasa de cotización cambió con el tiempo."""
    from src.core.pension.tasas import tasa_cotizacion_vigente

    # 1984: Ley 100/1993 aún no existía, era ~6.5%
    assert tasa_cotizacion_vigente(date(1984, 8, 1), ibc=14_610) == 0.065

    # 2000: Ley 100/1993 (6.5%). Ley 797/2003 entra en 2003
    assert tasa_cotizacion_vigente(date(2000, 1, 1), ibc=389_200) == 0.065

    # 2004: ya con Ley 797/2003 (7.125%)
    assert tasa_cotizacion_vigente(date(2004, 6, 1), ibc=500_000) == 0.07125

    # 2025 > 4 SMLMV: 16%
    tasa_2025 = tasa_cotizacion_vigente(date(2025, 7, 1), ibc=19_829_529)
    assert tasa_2025 == 0.16

    # 2025 con IBC bajo (< 4 SMLMV): régimen especial 8.5%
    tasa_bajo = tasa_cotizacion_vigente(date(2025, 7, 1), ibc=1_500_000)
    assert tasa_bajo == 0.085
