"""Regenera el reporte PDF de Francisco usando los datos IPC corregidos.

Uso:
    python scripts/generar_reporte_francisco.py
"""
from datetime import date
from pathlib import Path

from src.core.pension.calculator import PensionInput, calcular_pension
from src.core.pension.ibc import PeriodoCotizacion
from src.services.pdf_generator import generar_pdf, generar_html, guardar_html  # type: ignore


def main():
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

    input_data = PensionInput(
        fecha_nacimiento=date(1963, 12, 6),
        sexo="M",
        semanas_cotizadas=1289,
        periodos=periodos,
    )

    result = calcular_pension(input_data)

    print("=== Pensión estimada de Francisco (CASO REAL, IPC corregido Sep 2026) ===")
    print(f"Tiene derecho: {result.tiene_derecho}")
    print(f"Edad actual: {result.edad_actual} años")
    print(f"Semanas cotizadas: {result.semanas_cotizadas}")
    print(f"Ventana IBL: {result.ventana_utilizada}")
    print(f"IBL calculado: ${result.ibl_calculado:,.2f} COP/mes")
    print(f"Tasa reemplazo: {result.tasa_reemplazo*100:.1f}%")
    print(f"MESADA ESTIMADA: ${result.mesada_pensional:,.2f} COP/mes")
    print(f"Anual: ${result.mesada_pensional * 12:,.2f} COP")
    if result.observaciones:
        print("\nObservaciones:")
        for obs in result.observaciones:
            print(f"  - {obs}")

    # Generar HTML siempre (PDF es opcional si WeasyPrint está disponible)
    html_out = Path("reporte_francisco.html")
    guardar_html(result, html_out)
    print(f"\n[OK] HTML generado: {html_out.absolute()}")

    # Intentar PDF (WeasyPrint puede no estar instalado)
    try:
        pdf_out = Path("reporte_francisco.pdf")
        generar_pdf(result, pdf_out)
        print(f"[OK] PDF generado: {pdf_out.absolute()}")
    except Exception as e:
        print(f"[INFO] PDF no generado (WeasyPrint no disponible): {type(e).__name__}")
        print("       Para generar PDF: pip install weasyprint")


if __name__ == "__main__":
    main()
