"""Reporte profesional de estimacion pensional v3.

Diseno: tabla comparativa primero, detalle despues.
Sin tildes (ASCII compatible), generable como PDF con WeasyPrint.
"""
from datetime import date
from typing import Optional

from src.core.pension.calculator import PensionInput, PensionResult


def generar_reporte_profesional(
    input_data: PensionInput,
    result: PensionResult,
    simulador_oficial: Optional[float] = None,
) -> str:
    """Genera un reporte HTML conciso y profesional."""

    escenarios = _calcular_escenarios(input_data)
    max_mesada = max([e["mesada"] for e in escenarios] + [simulador_oficial or 0])
    grafico = _generar_grafico_escenarios(escenarios, simulador_oficial, max_mesada)

    estado_html = (
        '<span class="badge-ok">TIENE DERECHO</span>'
        if result.tiene_derecho
        else f'<span class="badge-warn">EN PROCESO - Faltan {result.semanas_faltantes} semanas</span>'
    )

    # Diferencia con simulador oficial (sí esta disponible)
    diferencia_html = ""
    if simulador_oficial:
        diff = simulador_oficial - result.mesada_pensional
        diff_pct = (diff / simulador_oficial * 100) if simulador_oficial > 0 else 0
        direccion = "mayor" if diff > 0 else "menor"
        diferencia_html = f"""
    <div class="diferencial">
        <strong>Diferencial con el simulador oficial de Colpensiones:</strong><br>
        El cálculo de Colpensiones proyecta una mesada de <strong>${simulador_oficial:,.0f} COP/mes</strong>
        (con ~1,800 semanas cotizadas), que es <strong>${abs(diff):,.0f} {direccion}</strong>
        ({diff_pct:+.1f}%) que nuestra estimacion de <strong>${result.mesada_pensional:,.0f} COP/mes</strong>
        (con las 1,289 semanas reales actuales).
        <br><br>
        <em>La diferencia principal se debe a que el simulador oficial asume que el solicitante
        continuara cotizando hasta completar 1,800 semanas (~511 semanas más, ~10 años),
        mientras que nuestro cálculo muestra la situacion actual.</em>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Reporte de Estimacion Pensional</title>
    <style>
        @page {{ size: A4; margin: 2cm; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a1a; line-height: 1.5; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1e3a5f; font-size: 24px; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #1e3a5f; font-size: 18px; margin-top: 25px; border-bottom: 1px solid #d1d5db; padding-bottom: 5px; }}
        h3 {{ color: #374151; font-size: 14px; margin-top: 15px; }}
        .meta {{ background: #f3f4f6; padding: 10px 15px; border-radius: 4px; font-size: 12px; color: #4b5563; margin: 15px 0; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }}
        .data-table th {{ background: #1e3a5f; color: white; padding: 8px 10px; text-align: left; font-weight: 600; }}
        .data-table td {{ padding: 6px 10px; border-bottom: 1px solid #e5e7eb; }}
        .value {{ font-weight: 600; color: #1e3a5f; text-align: right; font-family: 'Courier New', monospace; }}
        .highlight {{ background: #fef3c7; padding: 12px 15px; border-left: 4px solid #f59e0b; border-radius: 4px; margin: 12px 0; }}
        .result-box {{ background: #1e3a5f; color: white; padding: 20px; border-radius: 6px; margin: 15px 0; text-align: center; }}
        .result-box .number {{ font-size: 32px; font-weight: 700; color: #fbbf24; margin: 8px 0; }}
        .result-box .label {{ font-size: 13px; opacity: 0.9; }}
        .diferencial {{ background: #fff7ed; border: 1px solid #fed7aa; padding: 15px; border-radius: 4px; margin: 15px 0; font-size: 13px; }}
        .disclaimer {{ background: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 4px; margin: 15px 0; font-size: 12px; color: #991b1b; }}
        .supuestos {{ background: #f0f9ff; border: 1px solid #bae6fd; padding: 15px; border-radius: 4px; margin: 15px 0; font-size: 12px; }}
        .grafico {{ font-family: 'Courier New', monospace; background: #f9fafb; padding: 12px; border-radius: 4px; font-size: 11px; line-height: 1.4; white-space: pre; overflow-x: auto; }}
        .badge-ok {{ background: #d1fae5; color: #065f46; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
        .badge-warn {{ background: #fef3c7; color: #92400e; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
        .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #e5e7eb; font-size: 10px; color: #6b7280; text-align: center; }}
        .small {{ font-size: 12px; color: #6b7280; }}
    </style>
</head>
<body>

<h1>Reporte de Estimacion Pensional</h1>
<p class="small">Calculo estimativo segun normatividad colombiana vigente | {date.today().strftime("%d/%m/%Y")}</p>

<div class="meta">
    <strong>Fecha de emision:</strong> {date.today().strftime("%d/%m/%Y")} &nbsp;&nbsp;
    <strong>Motor v2.0:</strong> IPC indexado + Ley 797/2003 vigente
</div>

<h2>Datos del Solicitante</h2>
<table class="data-table">
    <tr><th>Concepto</th><th>Valor</th></tr>
    <tr><td>Fecha de nacimiento</td><td class="value">{input_data.fecha_nacimiento.strftime("%d/%m/%Y")}</td></tr>
    <tr><td>Sexo</td><td class="value">{"Masculino" if input_data.sexo == "M" else "Femenino"}</td></tr>
    <tr><td>Edad actual</td><td class="value">{result.edad_actual} años</td></tr>
    <tr><td>Edad de jubilación</td><td class="value">{result.edad_jubilacion} años</td></tr>
    <tr><td>Semanas cotizadas (Colpensiones)</td><td class="value">{result.semanas_cotizadas}</td></tr>
    <tr><td>Semanas faltantes</td><td class="value">{result.semanas_faltantes}</td></tr>
</table>

<h2>Resultado del Calculo (Situacion Actual)</h2>

<div class="result-box">
    <div class="label">Mesada pensional estimada con {result.semanas_cotizadas} semanas cotizadas</div>
    <div class="number">${result.mesada_pensional:,.0f} COP/mes</div>
    <div class="label">Equivalente anual: ${result.mesada_pensional * 12:,.0f} COP</div>
</div>

<div class="highlight">
    <strong>Estado del derecho:</strong> {estado_html}
</div>

<h3>Desglose</h3>
<table class="data-table">
    <tr><th>Componente</th><th>Valor</th></tr>
    <tr><td>IBL indexado al IPC</td><td class="value">${result.ibl_calculado:,.0f} COP/mes</td></tr>
    <tr><td>Ventana de cálculo</td><td class="value">{result.ventana_utilizada.replace('_', ' ')}</td></tr>
    <tr><td>Tasa de reemplazo</td><td class="value">{result.tasa_reemplazo * 100:.2f}%</td></tr>
    <tr><td>Formula</td><td class="value">IBL x Tasa</td></tr>
</table>
{diferencia_html}

<h2>Escenarios: Si Continua Cotizando</h2>
<p class="small">Proyeccion de mesada segun el número de semanas que alcanzaria al momento de jubilarse.</p>

<div class="grafico">{grafico}</div>

<table class="data-table">
    <tr>
        <th>Semanas</th>
        <th>Estado</th>
        <th>Tasa</th>
        <th>IBL indexado</th>
        <th>Mesada mensual</th>
        <th>Mesada anual</th>
    </tr>
    {_generar_tabla_escenarios(escenarios)}
    {f'<tr style="background: #fef3c7;"><td><strong>~1,800 (oficial)</strong></td><td colspan="3">Simulador oficial de Colpensiones</td><td class="value"><strong>${simulador_oficial:,.0f}</strong></td><td class="value"><strong>${simulador_oficial * 12:,.0f}</strong></td></tr>' if simulador_oficial else ''}
</table>

<h2>Marco Legal Aplicable</h2>

<h3>Normatividad</h3>
<ul>
    <li><strong>Ley 100 de 1993</strong> - Sistema General de Pensiones (Art. 34: edad y tasa)</li>
    <li><strong>Ley 797 de 2003</strong> - Reforma (Art. 10: nueva tasa de reemplazo)</li>
</ul>

<h3>Formula de la Tasa de Reemplazo (Ley 797/2003)</h3>
<p>Tasa base <strong>decreciente</strong> segun nivel de ingreso:</p>
<table class="data-table">
    <tr><th>Rango de ingreso (vs SMLMV)</th><th>Tasa base</th></tr>
    <tr><td>IBC <= 1 SMLMV</td><td class="value">65.0%</td></tr>
    <tr><td>1 < IBC <= 4 SMLMV</td><td class="value">60.0% - 65.0% (interpolado)</td></tr>
    <tr><td>4 < IBC <= 10 SMLMV</td><td class="value">55.0% - 60.0% (interpolado)</td></tr>
    <tr><td>IBC > 10 SMLMV</td><td class="value">55.0%</td></tr>
    <tr><td>Por cada 50 sem adicionales a 1,300</td><td class="value">+1.5%</td></tr>
    <tr><td><strong>Tope maximo</strong></td><td class="value"><strong>80.0%</strong></td></tr>
</table>

<h3>Requisitos para Pension de Vejez</h3>
<ul>
    <li>Edad: 62 años (hombres) / 57 años (mujeres)</li>
    <li>Semanas cotizadas: minimo 1,300 (Ley 797/2003)</li>
    <li>IBL: entre 1 SMLMV y 25 SMLMV (topes legales)</li>
</ul>

<div class="supuestos">
<h2>Supuestos del Calculo</h2>
<h3>Incluye</h3>
<ul>
    <li>Periodos cotizados (muestra representativa de la historia laboral)</li>
    <li>Indexacion al IPC historico del Banco de la República (1954-2026)</li>
    <li>Tasa decreciente por nivel de ingreso segun Ley 797/2003</li>
    <li>Incremento de 1.5% por cada 50 semanas sobre 1,300</li>
</ul>
<h3>NO incluye</h3>
<ul>
    <li>Aportes simultaneos en diferentes regimenes</li>
    <li>Licencias no remuneradas</li>
    <li>Regimen de transicion (personas con requisitos antes de 2003)</li>
    <li>Bono pensional ni indemnización sustitutiva</li>
    <li>Topes maximos/minimos legales (1/25 SMLMV)</li>
    <li>Rentabilidad de fondos AFP (solo RAIS)</li>
</ul>
</div>

<div class="disclaimer">
<h2>Disclaimers Importantes</h2>
<p><strong>1. Caracter informativo:</strong> Este reporte es informativo y educativo.
NO constituye asesoria legal, financiera ni actuarial. Para decisiones oficiales,
consulte con un profesional certificado.</p>

<p><strong>2. No vinculante:</strong> El cálculo NO es vinculante para Colpensiones ni
ninguna administradora. El cálculo oficial se realiza con la entidad mediante un
estudio personalizado de la historia laboral.</p>

<p><strong>3. Proyeccion, no certificado:</strong> Los valores son estimaciones
basadas en la normatividad vigente. El cálculo certificado lo hace Colpensiones.</p>

<p><strong>4. Limite temporal:</strong> La Ley 2381 de 2024 (reforma pensional) puede
modificar las condiciones. Consultar periodicamente.</p>
</div>

<h2>Recomendaciones</h2>
<ol>
    <li><strong>Solicitar estudio oficial en Colpensiones:</strong> El unico cálculo
    certificado es el que hace Colpensiones directamente.</li>
    <li><strong>Continuar cotizando:</strong> Cada 50 semanas adicionales incrementan
    la tasa en 1.5%. Llegar a 1,800 semanas asegura el maximo legal (80%).</li>
    <li><strong>Verificar historia laboral:</strong> Confirmar que todos los periodos
    esten correctamente registrados.</li>
    <li><strong>Considerar indemnización sustitutiva:</strong> Si no alcanza las 1,300
    semanas, tiene derecho a una devolucion de aportes.</li>
</ol>

<div class="footer">
    <p>Reporte generado por Pension Calculator v2.0 - Motor con IPC indexado y Ley 797/2003</p>
    <p>Desarrollado por Andres Giraldo - Julio 2026</p>
    <p>Documento informativo. Para decisiones oficiales, consulte con Colpensiones o un asesor certificado.</p>
</div>

</body>
</html>"""
    return html


def _generar_tabla_escenarios(escenarios) -> str:
    """Genera las filas de la tabla de escenarios."""
    rows = []
    for e in escenarios:
        sem = e["semanas"]
        estado_class = "badge-ok" if e["estado"] == "Califica" else "badge-warn"
        rows.append(f"""        <tr>
            <td><strong>{sem}</strong></td>
            <td><span class="{estado_class}">{e["estado"]}</span></td>
            <td class="value">{e["tasa"]*100:.2f}%</td>
            <td class="value">${e["ibl"]:,.0f}</td>
            <td class="value">${e["mesada"]:,.0f}</td>
            <td class="value">${e["mesada"]*12:,.0f}</td>
        </tr>""")
    return "\n".join(rows)


def _calcular_escenarios(input_data: PensionInput) -> list:
    """Calcula varios escenarios de semanas para el grafico."""
    from src.core.pension.calculator import calcular_pension

    escenarios = []
    for sem in [1289, 1300, 1350, 1400, 1500, 1600, 1700, 1800]:
        p = PensionInput(
            fecha_nacimiento=input_data.fecha_nacimiento,
            sexo=input_data.sexo,
            semanas_cotizadas=sem,
            periodos=input_data.periodos,
            regimen=input_data.regimen,
            fecha_referencia_ibl=input_data.fecha_referencia_ibl,
        )
        r = calcular_pension(p)
        escenarios.append({
            "semanas": sem,
            "estado": "Califica" if r.tiene_derecho else "Faltan",
            "tasa": r.tasa_reemplazo,
            "ibl": r.ibl_calculado,
            "mesada": r.mesada_pensional,
        })
    return escenarios


def _generar_grafico_escenarios(escenarios, simulador_oficial, max_valor) -> str:
    """Genera un grafico de barras ASCII con los escenarios."""
    lines = []
    lines.append("Mesada pensional por semanas cotizadas")
    lines.append("=" * 70)

    for e in escenarios:
        sem = e["semanas"]
        mesada = e["mesada"]
        ancho = int((mesada / max_valor) * 50) if max_valor > 0 else 0
        barra = "#" * ancho
        lines.append(f"  {sem:>5} sem | {barra:<50} ${mesada:>13,.0f}")

    lines.append("-" * 70)

    if simulador_oficial:
        ancho = int((simulador_oficial / max_valor) * 50)
        barra = "=" * ancho
        lines.append(f"  Oficial | {barra:<50} ${simulador_oficial:>13,.0f}")

    lines.append("=" * 70)
    return "\n".join(lines)