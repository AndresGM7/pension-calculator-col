"""Caso Francisco: comparación RPM vs RAIS con datos reales.

Genera reporte detallado de qué pension tendría Francisco en cada regimen.
"""
from datetime import date

from src.core.pension.comparacion import comparar_regimenes
from src.core.pension.ibc import PeriodoCotizacion


def main():
    # Historia laboral de Francisco (mismos periodos que test_francisco.py)
    periodos = [
        PeriodoCotizacion(date(1984, 8, 28), date(1985, 1, 16), 14_610),
        PeriodoCotizacion(date(1996, 1, 1), date(1996, 5, 31), 142_125),
        PeriodoCotizacion(date(1997, 1, 1), date(1997, 8, 31), 164_000),
        PeriodoCotizacion(date(1998, 5, 1), date(1998, 11, 30), 209_000),
        PeriodoCotizacion(date(1999, 3, 1), date(1999, 12, 31), 264_000),
        PeriodoCotizacion(date(2000, 1, 1), date(2000, 4, 30), 320_000),
        PeriodoCotizacion(date(2000, 5, 1), date(2000, 7, 31), 389_200),
        PeriodoCotizacion(date(2025, 1, 1), date(2025, 3, 31), 15_348_653),
        PeriodoCotizacion(date(2025, 4, 1), date(2025, 6, 30), 18_502_790),
        PeriodoCotizacion(date(2025, 7, 1), date(2025, 9, 30), 19_829_529),
        PeriodoCotizacion(date(2025, 10, 1), date(2025, 12, 31), 16_783_393),
    ]

    print("=" * 80)
    print("CASO FRANCISCO LUIS GIRALDO GUTIERREZ - Comparacion RPM vs RAIS")
    print("=" * 80)
    print(f"Fecha de nacimiento: 06/12/1963")
    print(f"Edad actual: 62 anos")
    print(f"Sexo: Masculino")
    print(f"Semanas cotizadas: 1,289")
    print(f"Periodos en historia laboral: {len(periodos)}")
    print()

    resultado = comparar_regimenes(
        fecha_nacimiento=date(1963, 12, 6),
        sexo="M",
        semanas_cotizadas=1289,
        periodos=periodos,
        regimen_rpm="LEY_797_2003",
    )

    # === RPM ===
    print("--- RPM (Colpensiones) ---")
    print(f"Tiene derecho: {'SI' if resultado.rpm_tiene_derecho else 'NO (faltan semanas)'}")
    print(f"IBL: ${resultado.rpm_ibl:,.0f} COP/mes")
    print(f"Tasa reemplazo: {resultado.rpm_tasa*100:.1f}%")
    print(f"MESADA RPM: ${resultado.rpm_mesada:,.0f} COP/mes")
    print(f"           ${resultado.rpm_mesada*12:,.0f} COP/anio")
    print()

    # === RAIS ===
    print("--- RAIS (AFPs privadas) ---")
    print(f"Saldo acumulado proyectado: ${resultado.rais_saldo_final:,.0f} COP")
    print()
    print("Mesada esperada por escenario de rentabilidad:")
    for escenario in resultado.rais_escenarios:
        print(f"  {escenario['nombre']} ({escenario['rentabilidad_anual']*100:.1f}% anual):")
        print(f"    Renta vitalicia: ${escenario['mesada_vitalicia']:,.0f}/mes")
        print(f"    Retiro programado: ${escenario['mesada_retiro_programado']:,.0f}/mes")
    print()

    # === Comparacion ===
    print("--- ANALISIS COMPARATIVO ---")
    print(f"Recomendacion: {resultado.regimen_recomendado}")
    print(f"Diferencia mensual (RAIS moderado - RPM): ${resultado.diferencia_mensual:,.0f}")
    print(f"Diferencia porcentual: {resultado.diferencia_porcentual:.1f}%")
    print()
    print("VENTAJAS RPM:")
    for v in resultado.ventajas_rpm:
        print(f"  + {v}")
    print()
    print("VENTAJAS RAIS:")
    for v in resultado.ventajas_rais:
        print(f"  + {v}")
    print()
    print("OBSERVACIONES:")
    for obs in resultado.observaciones:
        print(f"  - {obs}")


if __name__ == "__main__":
    main()
