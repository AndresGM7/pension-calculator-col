"""IBC — Ingreso Base de Cotización.

Este módulo representa el SALARIO sobre el cual una persona cotizó a pensión
en un periodo específico. Sale directamente de la historia laboral.

Concepto simple: cada mes que trabajaste, hubo un salario, y un porcentaje
de ese salario (típicamente 7.125% antes de 2025) se destinó a tu cuenta
de pensión.

Ejemplo de Francisco (1984):
- Salario reportado: $14.610
- Porcentaje cotizado: 7.125%
- Aporte mensual: $14.610 × 0.07125 = $1.040

A lo largo de 40 años, una persona tiene MUCHOS IBC diferentes.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class PeriodoCotizacion:
    """Un periodo donde la persona cotizó a pensión.
    
    Atributos:
        fecha_inicio: primer día del periodo
        fecha_fin: último día del periodo
        ibc: salario mensual sobre el que se cotizó (COP)
    """
    fecha_inicio: date
    fecha_fin: date
    ibc: float


def semanas_del_periodo(periodo: PeriodoCotizacion) -> float:
    """Calcula cuántas semanas cotizó un periodo.
    
    Una semana = 7 días. Si trabajaste del 01/01/2020 al 31/03/2020,
    son aproximadamente 13 semanas (90 días / 7).
    
    Esto se usa para validar contra el reporte oficial de Colpensiones.
    """
    dias = (periodo.fecha_fin - periodo.fecha_inicio).days
    return dias / 7


def validar_periodo(periodo: PeriodoCotizacion) -> tuple[bool, str]:
    """Valida que un periodo sea correcto antes de calcular."""
    if periodo.fecha_fin < periodo.fecha_inicio:
        return False, "La fecha fin no puede ser anterior a la fecha inicio"
    if periodo.ibc <= 0:
        return False, "El IBC debe ser positivo"
    return True, ""


# === Ejemplo de uso ===
if __name__ == "__main__":
    # Primer periodo de Francisco (28/08/1984 - 16/01/1985)
    p1 = PeriodoCotizacion(
        fecha_inicio=date(1984, 8, 28),
        fecha_fin=date(1985, 1, 16),
        ibc=14_610,
    )
    ok, error = validar_periodo(p1)
    print(f"Periodo válido: {ok}")
    if ok:
        semanas = semanas_del_periodo(p1)
        print(f"Semanas: {semanas:.2f}")
        aporte = p1.ibc * 0.07125
        print(f"Aporte mensual: ${aporte:,.2f} COP")
