"""Modulo de IPC (Indice de Precios al Consumidor) Colombiano.

FUENTE PRINCIPAL: Banco de la Republica de Colombia
Archivo CSV: data/IPC_Indice de Precios al Consumidor.csv
- IPC mensual desde 1954 hasta junio 2026
- Base 100 = diciembre 2018
- 864 registros

FUENTES SECUNDARIAS:
- DANE: variaciones porcentuales (archivo XLSX)

FORMULA DE INDEXACION:
    IBC_actualizado = IBC_historico * (IPC_referencia / IPC_periodo)
"""
import csv
from datetime import date
from pathlib import Path
from typing import Dict, Optional


# Cache del IPC
_IPC_CACHE: Optional[Dict[str, float]] = None


def cargar_ipc(archivo_csv: str | Path = None) -> Dict[str, float]:
    """Carga IPC mensual desde el CSV del Banco de la Republica.

    Returns:
        Dict con key = fecha ISO (YYYY-MM-DD) y value = IPC
    """
    global _IPC_CACHE
    if _IPC_CACHE is not None:
        return _IPC_CACHE

    if archivo_csv is None:
        # Buscar el CSV en ubicaciones comunes
        candidatos = [
            Path("data/IPC_Índice de Precios al Consumidor.csv"),
            Path("../data/IPC_Índice de Precios al Consumidor.csv"),
            Path(__file__).parent.parent.parent.parent / "data" / "IPC_Índice de Precios al Consumidor.csv",
            Path("C:/work/Projects/pension-calculator/data/IPC_Índice de Precios al Consumidor.csv"),
        ]
        ruta = None
        for c in candidatos:
            if c.exists():
                ruta = c
                break
        if ruta is None:
            ruta = candidatos[0]
    else:
        ruta = Path(archivo_csv)

    datos = {}
    if not ruta.exists():
        return datos

    with open(ruta, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            periodo = row.get("Periodo(MMM, AAAA)", "")
            try:
                valor = float(row.get("Índice de Precios al Consumidor (IPC)", "0"))
                # Convertir fecha de "AAAA/MM/DD" a ISO
                fecha_iso = periodo.replace("/", "-")
                datos[fecha_iso] = valor
            except (ValueError, AttributeError):
                continue

    _IPC_CACHE = datos
    return datos


def obtener_ipc(fecha: date, archivo_csv: str | Path = None) -> float:
    """Obtiene el IPC de un mes especifico.

    Args:
        fecha: fecha del mes a consultar

    Returns:
        IPC del mes, o 0 si no se encuentra
    """
    datos = cargar_ipc(archivo_csv)
    # El CSV tiene fechas como "1954-07-31" (ultimo dia del mes)
    # Construimos todas las claves posibles del mes y buscamos
    anio_mes = fecha.strftime("%Y-%m")
    for clave in datos.keys():
        if clave.startswith(anio_mes):
            return datos[clave]
    return 0.0


def indexar_ibc(
    ibc_historico: float,
    fecha_historica: date,
    fecha_referencia: date | None = None,
    archivo_csv: str | Path = None,
) -> float:
    """Actualiza un IBC historico a valor presente usando IPC.

    Formula: IBC_actualizado = IBC_historico * (IPC_ref / IPC_periodo)

    Args:
        ibc_historico: IBC en pesos de la fecha historica
        fecha_historica: fecha del IBC original
        fecha_referencia: fecha a la que se quiere actualizar (default: hoy)

    Returns:
        IBC en pesos de la fecha de referencia
    """
    if fecha_referencia is None:
        fecha_referencia = date.today()

    ipc_historico = obtener_ipc(fecha_historica, archivo_csv)
    ipc_referencia = obtener_ipc(fecha_referencia, archivo_csv)

    if ipc_historico == 0 or ipc_referencia == 0:
        # No tenemos datos, devolver sin indexar
        return ibc_historico

    factor = ipc_referencia / ipc_historico
    return ibc_historico * factor


# === Ejemplo de uso completo ===
if __name__ == "__main__":
    from src.core.pension.ibc import PeriodoCotizacion
    from src.core.pension.legislacion import calcular_tasa_reemplazo_vigente
    from src.core.pension.ibc import PeriodoCotizacion
    from src.core.pension.legislacion import calcular_tasa_reemplazo_vigente

    # Cargar IPC
    datos = cargar_ipc()
    fecha_ref = date(2026, 6, 30)  # Ultima fecha disponible en CSV
    print(f"IPC cargado: {len(datos)} registros")
    print(f"Primer registro: 1954-07-31 = {datos.get('1954-07-31', 'N/A')}")
    print(f"Ultimo registro: {max(datos.keys())} = {datos[max(datos.keys())]}")
    print()

    # Indexar IBC de Francisco
    print("=== Indexacion de IBC de Francisco ===")
    print(f"  $14.610 (1984-08-28) -> ${indexar_ibc(14_610, date(1984, 8, 28), fecha_ref):,.0f}")
    print(f"  $389.200 (2000-05-01) -> ${indexar_ibc(389_200, date(2000, 5, 1), fecha_ref):,.0f}")
    print(f"  $19.829.529 (2025-07-01) -> ${indexar_ibc(19_829_529, date(2025, 7, 1), fecha_ref):,.0f}")
    print()

    # Calculo completo de Francisco
    print("=== Calculo REAL con IPC indexado ===")
    periodos = [
        PeriodoCotizacion(date(1984, 8, 28), date(1985, 1, 16), 14_610),
        PeriodoCotizacion(date(2000, 5, 1), date(2000, 7, 31), 389_200),
        PeriodoCotizacion(date(2025, 7, 1), date(2025, 9, 30), 19_829_529),
    ]

    # Indexar cada periodo
    periodos_indexados = []
    for p in periodos:
        ibc_idx = indexar_ibc(p.ibc, date(p.fecha_fin.year, p.fecha_fin.month, 1), fecha_ref)
        periodos_indexados.append(PeriodoCotizacion(p.fecha_inicio, p.fecha_fin, ibc_idx))
        print(f"  ${p.ibc:,.0f} ({p.fecha_inicio.year}) -> ${ibc_idx:,.0f} (2026)")

    ibl_promedio = sum(p.ibc for p in periodos_indexados) / len(periodos_indexados)
    print(f"\nIBL indexado promedio: ${ibl_promedio:,.0f}")

    tasa = calcular_tasa_reemplazo_vigente(1289, ibl_promedio)
    print(f"Tasa de reemplazo (1,289 semanas, no califica): {tasa*100:.1f}%")
    tasa = calcular_tasa_reemplazo_vigente(1300, ibl_promedio)
    print(f"Tasa de reemplazo (1,300 semanas, minimo): {tasa*100:.1f}%")
    tasa = calcular_tasa_reemplazo_vigente(1500, ibl_promedio)
    print(f"Tasa de reemplazo (1,500 semanas): {tasa*100:.1f}%")
    print(f"  Tope maximo: 80%")
