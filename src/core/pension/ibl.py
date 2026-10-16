"""IBL — Ingreso Base de Liquidación.

Concepto: NO es un número que existe en la historia laboral. Es un
CÁLCULO que se hace sobre los IBC de un periodo, según cuántas semanas
cotizó la persona en total.

Reglas oficiales (Ley 797/2003, Art. 18 que modifica Art. 21 Ley 100):

    Semanas cotizadas | Ventana de IBC a promediar
    ------------------+----------------------------
    1,300 a 1,800     | últimos 10 años
    1,800 a 2,200     | últimos 20 años
    más de 2,200      | toda la vida laboral

Para nuestro MVP inicial, asumimos que el IBL ya viene calculado
(o se calcula trivialmente como promedio simple de los últimos N años).

FUTURO: implementar las reglas complejas con indexación al IPC.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from statistics import mean
from typing import List

from src.core.pension.ibc import PeriodoCotizacion


def ventana_por_semanas(semanas_totales: int) -> int:
    """Devuelve cuántos años se promedian según las semanas cotizadas.
    
    Args:
        semanas_totales: total de semanas cotizadas por la persona
    
    Returns:
        Cantidad de años de IBC a promediar
    """
    if semanas_totales < 1_300:
        # No tiene derecho, pero igual mostramos proyección
        return 10  # últimos 10 años como referencia
    elif semanas_totales < 1_800:
        return 10
    elif semanas_totales < 2_200:
        return 20
    else:
        # Más de 20 años — toda la vida laboral
        return None  # significa "toda la historia"


def filtrar_periodos_recientes(
    periodos: List[PeriodoCotizacion],
    anos_ventana: int,
    fecha_referencia: date | None = None,
) -> List[PeriodoCotizacion]:
    """Filtra los periodos que caen dentro de la ventana de años.
    
    Args:
        periodos: lista completa de periodos de cotización
        años_ventana: cantidad de años hacia atrás (None = todos)
        fecha_referencia: desde qué fecha contar hacia atrás (default: hoy)
    
    Returns:
        Subset de periodos que caen en la ventana
    """
    if fecha_referencia is None:
        fecha_referencia = date.today()
    
    if anos_ventana is None:
        # Toda la vida laboral
        return periodos
    
    fecha_inicio_ventana = fecha_referencia - timedelta(days=365 * anos_ventana)

    # Recortar cada periodo a la ventana de tiempo (interseccion con ventana)
    # Esto evita que periodos largos (ej: 1990-2025 con ventana 10y) se incluyan
    # completos, sesgando el IBL hacia arriba. Solo la fraccion dentro de la
    # ventana debe contar para el promedio.
    filtrados = []
    for p in periodos:
        # Validar periodo: fechas validas y IBC positivo
        if p.fecha_inicio > p.fecha_fin:
            # Periodo invertido, lo saltamos silenciosamente
            continue
        if p.ibc <= 0:
            # IBC cero o negativo (licencia no remunerada, error), excluir
            continue

        # Calcular interseccion con la ventana
        inicio = max(p.fecha_inicio, fecha_inicio_ventana)
        fin = min(p.fecha_fin, fecha_referencia)

        # Si hay interseccion (el periodo cae al menos parcialmente en ventana)
        if fin > inicio:
            filtrados.append(PeriodoCotizacion(
                fecha_inicio=inicio,
                fecha_fin=fin,
                ibc=p.ibc,
            ))

    return filtrados


def calcular_ibl(
    periodos: List[PeriodoCotizacion],
    semanas_totales: int,
    fecha_referencia: date | None = None,
) -> float:
    """Calcula el IBL según las reglas de la Ley 797/2003.
    
    Args:
        periodos: lista completa de periodos cotizados (de la historia laboral)
        semanas_totales: total de semanas cotizadas
        fecha_referencia: fecha de cálculo (default: hoy)
    
    Returns:
        IBL promedio mensual en COP
    """
    if not periodos:
        return 0.0
    
    anos = ventana_por_semanas(semanas_totales)
    periodos_relevantes = filtrar_periodos_recientes(
        periodos, anos, fecha_referencia
    )
    
    if not periodos_relevantes:
        return 0.0
    
    # Promedio simple de IBC de los periodos relevantes
    # NOTA: en producción habría que ponderar por duración del periodo,
    # actualizar valores por IPC, etc. Para MVP, promedio simple.
    ibcs = [p.ibc for p in periodos_relevantes]
    return mean(ibcs)


# === Ejemplo de uso con Francisco ===
if __name__ == "__main__":
    # Solo algunos periodos representativos de Francisco
    periodos_francisco = [
        PeriodoCotizacion(date(1984, 8, 28), date(1985, 1, 16), 14_610),
        PeriodoCotizacion(date(1995, 10, 1), date(1995, 10, 31), 118_933),
        PeriodoCotizacion(date(1998, 5, 1), date(1998, 5, 31), 209_000),
        PeriodoCotizacion(date(2000, 5, 1), date(2000, 7, 31), 389_200),
        # Los reales son muchos más — esto es solo muestra
    ]
    
    # Francisco tiene ~62 años, > 1,300 semanas cotizadas
    semanas_francisco = 1_800  # estimación
    
    ibl = calcular_ibl(periodos_francisco, semanas_francisco)
    print(f"IBL estimado de Francisco: ${ibl:,.2f} COP/mes")
