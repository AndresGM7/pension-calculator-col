"""Actualiza los archivos JSON con datos oficiales frescos.

USO:
    1. Bajar de Banrep:
       - https://suameca.banrep.gov.co/graficador-interactivo/grafica/15416
         Click derecho "Descargar datos" -> guarda como Downloads/chart.csv
       - https://suameca.banrep.gov.co/estadisticas-economicas/encuestas
         Click derecho "Descargar series historicas" -> Downloads/series_historicas.xlsx

    2. Bajar de Colfondos:
       - https://www.colfondos.com.co/dxp/personas/pensiones-obligatorias/conoce-mas/cifras?tab=0
         Tabla "Rentabilidades" -> guardar valores en data/raw/colfondos_carta_circular.txt

    3. Ejecutar este script:
       python scripts/actualizar_datos_oficiales.py

El script:
- Lee Downloads/chart.csv -> actualiza smlmv_historico_anual_cop en macro_proyecciones.json
- Lee Downloads/series_historicas.xlsx -> actualiza expectativas_inflacion_historicas_banrep
- Lee data/raw/colfondos_carta_circular.txt -> actualiza rentabilidades_acumuladas_efectivas_anuales_tir
"""
import csv
import json
import os
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
except ImportError:
    print("[ERROR] Necesitas instalar openpyxl: pip install openpyxl")
    raise


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "macro_proyecciones.json"
RAIS_FILE = ROOT / "data" / "rais_rentabilidades.json"
RAW_DIR = ROOT / "data" / "raw"
DOWNLOADS = Path.home() / "Downloads"


def buscar_archivo(pattern: str, search_dirs: list[Path]) -> Path | None:
    """Busca un archivo que matchea el patron en los directorios."""
    for dir_ in search_dirs:
        if not dir_.exists():
            continue
        for archivo in dir_.glob(pattern):
            return archivo
        # Busqueda mas flexible
        for archivo in dir_.iterdir():
            if re.search(pattern, archivo.name, re.IGNORECASE):
                return archivo
    return None


def actualizar_smlmv(data: dict) -> bool:
    """Actualiza SMLMV desde chart.csv del Banrep."""
    chart = buscar_archivo("chart.csv", [DOWNLOADS])
    if chart is None:
        print("[SKIP] SMLMV: chart.csv no encontrado en Downloads")
        return False

    print(f"[OK] SMLMV: leyendo {chart}")
    smlmv = {}
    with open(chart, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row and len(row) >= 2:
                fecha = row[0]
                year = int(fecha.split("/")[0])
                valor = int(row[1])
                smlmv[str(year)] = valor

    # Actualizar
    if "smlmv_historico_anual_cop" not in data:
        data["smlmv_historico_anual_cop"] = {}

    for year, valor in smlmv.items():
        # Eliminar comentario previo si existe
        for key in list(data["smlmv_historico_anual_cop"].keys()):
            if key.startswith("_"):
                continue
            if key == year:
                break
        data["smlmv_historico_anual_cop"][year] = valor

    print(f"[OK] SMLMV: {len(smlmv)} anos actualizados")
    return True


def actualizar_expectativas_inflacion(data: dict) -> bool:
    """Actualiza expectativas de inflacion desde series_historicas.xlsx."""
    archivo = buscar_archivo("series_historicas", [DOWNLOADS])
    if archivo is None:
        print("[SKIP] Expectativas: series_historicas.xlsx no encontrado")
        return False

    print(f"[OK] Expectativas: leyendo {archivo}")
    wb = openpyxl.load_workbook(archivo, data_only=True)

    if 'INFLACION_TOTAL' not in wb.sheetnames:
        print("[ERROR] Sheet INFLACION_TOTAL no encontrado")
        return False

    ws = wb['INFLACION_TOTAL']

    exp_12m = defaultdict(list)
    exp_24m = defaultdict(list)
    exp_60m = defaultdict(list)
    ultimo = None

    for row in ws.iter_rows(min_row=5, values_only=True):
        fecha = row[0]
        if isinstance(fecha, datetime):
            if isinstance(row[7], (int, float)) and row[7] > 0:
                exp_12m[fecha.year].append(row[7])
            if isinstance(row[13], (int, float)) and row[13] > 0:
                exp_24m[fecha.year].append(row[13])
            if isinstance(row[16], (int, float)) and row[16] > 0:
                exp_60m[fecha.year].append(row[16])
            # Guardar el ultimo dato
            if isinstance(row[7], (int, float)) and row[7] > 0:
                ultimo = {
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "inflacion_12m_promedio": row[7],
                    "inflacion_diciembre_anio_sgte_promedio": (
                        row[10] if isinstance(row[10], (int, float)) else None
                    ),
                    "inflacion_24m_promedio": (
                        row[13] if isinstance(row[13], (int, float)) else None
                    ),
                    "inflacion_60m_promedio": (
                        row[16] if isinstance(row[16], (int, float)) else None
                    ),
                }

    # Promedios anuales
    prom_12m = {str(y): round(sum(v)/len(v), 4) for y, v in exp_12m.items()}
    prom_24m = {str(y): round(sum(v)/len(v), 4) for y, v in exp_24m.items()}
    prom_60m = {str(y): round(sum(v)/len(v), 4) for y, v in exp_60m.items()}

    data["expectativas_inflacion_historicas_banrep"] = {
        "_fuente": "Banrep series_historicas.xlsx - Encuesta mensual de expectativas economicas",
        "_url": "https://suameca.banrep.gov.co/estadisticas-economicas/encuestas",
        "_metodologia": "Promedio anual de las expectativas de inflacion a 12, 24 y 60 meses reportadas mensualmente",
        "_cobertura": f"Sep 2003 - {ultimo['fecha'] if ultimo else 'N/A'}",
        "promedio_anual_inflacion_12m": prom_12m,
        "promedio_anual_inflacion_24m": prom_24m,
        "promedio_anual_inflacion_60m": prom_60m,
        f"ultimo_dato_{ultimo['fecha'].replace('-', '_') if ultimo else 'ultimo'}": ultimo or {},
    }

    print(f"[OK] Expectativas: {len(prom_12m)} anos actualizados")
    return True


def main():
    print("=" * 70)
    print("ACTUALIZADOR DE DATOS OFICIALES")
    print("=" * 70)
    print()

    # Crear carpeta data/raw si no existe
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar JSONs actuales
    if not DATA_FILE.exists():
        print(f"[ERROR] {DATA_FILE} no existe. Creando uno vacio.")
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        macro_data = json.load(f)

    # Actualizar timestamp
    macro_data["ultima_actualizacion"] = datetime.now().strftime("%Y-%m-%d")

    # Actualizar SMLMV
    print("\n--- Actualizando SMLMV desde Banrep ---")
    actualizar_smlmv(macro_data)

    # Actualizar expectativas de inflacion
    print("\n--- Actualizando expectativas de inflacion desde Banrep ---")
    actualizar_expectativas_inflacion(macro_data)

    # Guardar
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(macro_data, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] {DATA_FILE} actualizado")
    print()
    print("Proximos pasos:")
    print("  1. Verificar manualmente los valores")
    print("  2. Correr tests: PYTHONPATH=. python -m pytest tests/ -v")
    print("  3. Si actualizaste datos de Colfondos, edita data/rais_rentabilidades.json")
    print("     manualmente (formato en el archivo)")


if __name__ == "__main__":
    main()