"""Generador de PDFs de pensiones.

Usa Jinja2 para el template HTML + WeasyPrint para convertir a PDF.
Es el estandar de la industria para generar reportes en Python.
"""
from datetime import date
from pathlib import Path

from jinja2 import Template

from src.core.pension.calculator import PensionResult


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reporte de Pension - {{ fecha_reporte }}</title>
    <style>
        body {
            font-family: 'Helvetica', Arial, sans-serif;
            color: #333;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .info-box {
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
        }
        .info-box.apto {
            border-left-color: #27ae60;
            background-color: #e8f5e9;
        }
        .info-box.no-apto {
            border-left-color: #e74c3c;
            background-color: #fdecea;
        }
        .numero-grande {
            font-size: 36px;
            font-weight: bold;
            color: #27ae60;
        }
        table {
            width: 100%%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 11px;
            color: #777;
        }
    </style>
</head>
<body>
    <h1>Reporte de Estimacion de Pension</h1>
    <p><strong>Fecha del reporte:</strong> {{ fecha_reporte }}</p>
    <p><strong>Regimen aplicado:</strong> {{ resultado.regimen_aplicable }}</p>

    <div class="info-box {{ 'apto' if resultado.tiene_derecho else 'no-apto' }}">
        <h2>{{ 'APTO PARA PENSION' if resultado.tiene_derecho else 'NO APTO TODAVIA' }}</h2>
        {% if resultado.tiene_derecho %}
            <p>El solicitante cumple con los requisitos legales para acceder a la pension de vejez.</p>
        {% else %}
            <p>El solicitante aun no cumple con todos los requisitos. Ver detalles abajo.</p>
        {% endif %}
    </div>

    <h2>Datos del Solicitante</h2>
    <table>
        <tr>
            <th>Concepto</th>
            <th>Valor</th>
        </tr>
        <tr>
            <td>Edad actual</td>
            <td>{{ resultado.edad_actual }} años</td>
        </tr>
        <tr>
            <td>Edad de jubilacion</td>
            <td>{{ resultado.edad_jubilacion }} años</td>
        </tr>
        <tr>
            <td>Semanas cotizadas</td>
            <td>{{ resultado.semanas_cotizadas }}</td>
        </tr>
        <tr>
            <td>Semanas faltantes</td>
            <td>{{ resultado.semanas_faltantes }}</td>
        </tr>
    </table>

    <h2>Calculo del IBL (Ingreso Base de Liquidacion)</h2>
    <div class="info-box">
        <p><strong>Ventana utilizada:</strong> {{ resultado.ventana_utilizada.replace('_', ' ') }}</p>
        <p><strong>IBL promedio:</strong> <span class="numero-grande">${{ "{:,.0f}".format(resultado.ibl_calculado) }} COP/mes</span></p>
        <p><em>Promedio del IBC reportado durante la ventana legal correspondiente.</em></p>
    </div>

    <h2>Tasa de Reemplazo</h2>
    <table>
        <tr>
            <th>Rango de semanas</th>
            <th>Tasa</th>
        </tr>
        <tr style="background-color: #fff3cd;">
            <td>{{ resultado.semanas_cotizadas }} semanas (su caso)</td>
            <td><strong>{{ "{:.1f}".format(resultado.tasa_reemplazo * 100) }}% del IBL</strong></td>
        </tr>
    </table>

    <h2>Mesada Pensional Estimada</h2>
    <div class="info-box apto">
        <p>Segun los parametros calculados:</p>
        <p class="numero-grande">${{ "{:,.0f}".format(resultado.mesada_pensional) }} COP/mes</p>
        <p><strong>Equivalente anual:</strong> ${{ "{:,.0f}".format(resultado.mesada_pensional * 12) }} COP/ano</p>
        <p><em>Este es un calculo estimado. El valor oficial lo determina Colpensiones o su AFP.</em></p>
    </div>

    {% if resultado.observaciones %}
    <h2>Observaciones</h2>
    <ul>
    {% for obs in resultado.observaciones %}
        <li>{{ obs }}</li>
    {% endfor %}
    </ul>
    {% endif %}

    <h2>Marco Legal Aplicado</h2>
    <p>Este calculo se realiza segun la Ley 797 de 2003, que modifica el Articulo 34 de la Ley 100 de 1993.</p>
    <p>Requisitos: 1,300 semanas cotizadas (minimo), 62 años (hombres) o 57 años (mujeres).</p>
    <p>Tasa de reemplazo: 40%% a 80%% del IBL segun la tabla oficial de tramos.</p>

    <div class="footer">
        <p>Reporte generado por Pension Calculator MVP v0.1.0</p>
        <p>Andres Giraldo - Buenos Aires, Argentina</p>
        <p><em>Este documento es informativo. No constituye asesoria legal ni financiera.</em></p>
    </div>
</body>
</html>
"""


def generar_html(resultado: PensionResult) -> str:
    """Genera el HTML del reporte a partir del resultado del calculo."""
    template = Template(HTML_TEMPLATE)
    return template.render(
        resultado=resultado,
        fecha_reporte=date.today().isoformat(),
    )


def guardar_html(resultado: PensionResult, path: str | Path) -> Path:
    """Guarda el HTML generado en un archivo."""
    path = Path(path)
    html = generar_html(resultado)
    path.write_text(html, encoding="utf-8")
    return path


def generar_pdf(resultado: PensionResult, path: str | Path) -> Path:
    """Genera un PDF del reporte.

    NOTA: requiere weasyprint instalado.
    Si no esta instalado, genera HTML en su lugar.
    """
    path = Path(path)
    html = generar_html(resultado)

    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(target=str(path))
        return path
    except ImportError:
        # Fallback: guardar como HTML
        html_path = path.with_suffix(".html")
        html_path.write_text(html, encoding="utf-8")
        return html_path


# === Ejemplo de uso ===
if __name__ == "__main__":
    from src.core.pension.calculator import PensionInput, calcular_pension
    from src.core.pension.ibc import PeriodoCotizacion

    periodos = [
        PeriodoCotizacion(date(2025, 1, 1), date(2025, 3, 31), 15_348_653),
        PeriodoCotizacion(date(2025, 4, 1), date(2025, 6, 30), 18_502_790),
        PeriodoCotizacion(date(2025, 7, 1), date(2025, 9, 30), 19_829_529),
    ]

    input_data = PensionInput(
        fecha_nacimiento=date(1963, 12, 6),
        sexo="M",
        semanas_cotizadas=1700,
        periodos=periodos,
    )

    result = calcular_pension(input_data)

    # Generar HTML (funciona sin weasyprint)
    output_path = generar_pdf(result, "reporte_francisco.pdf")
    print(f"Reporte guardado en: {output_path}")
