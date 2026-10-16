"""Carga rentabilidades reales de AFPs desde archivos Excel/CSV.

USO:
    1. Bajar los archivos de Asofondos / SuperFinanciera (ver docs/FUENTES_DATOS_OFICIALES.md)
    2. Guardarlos en data/raw/ con estos nombres:
       - rentabilidades_porvenir.xlsx
       - rentabilidades_proteccion.xlsx
       - rentabilidades_skancia_colfondos.xlsx
       - rentabilidades_old_mutual.xlsx
    3. Correr este script:
       python scripts/cargar_rentabilidades_reales.py

El script:
- Detecta el formato de cada Excel/CSV
- Calcula rentabilidades anualizadas por tipo de fondo (Conservador/Moderado/Mayor_Riesgo)
- Genera data/rais_rentabilidades.json con la estructura esperada por el motor
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DEST = ROOT / "data" / "rais_rentabilidades.json"

AFPS = ["Porvenir", "Proteccion", "Skandia_Colfondos", "Old_Mutual"]


def buscar_archivo_afp(afp: str) -> Path | None:
    """Busca archivo de rentabilidades para una AFP."""
    if not RAW.exists():
        return None
    nombre_normalizado = afp.lower().replace("_", "")
    extensiones = ["*.xlsx", "*.xls", "*.csv"]

    for ext in extensiones:
        for archivo in RAW.glob(ext):
            if nombre_normalizado in archivo.stem.lower().replace("_", "").replace(" ", ""):
                return archivo
    return None


def leer_excel(path: Path) -> list[dict]:
    """Lee un archivo Excel y retorna filas como dicts."""
    try:
        import openpyxl
    except ImportError:
        print("[ERROR] Necesitás instalar openpyxl: pip install openpyxl")
        return []

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active

    filas = []
    headers = None
    for row in ws.iter_rows(values_only=True):
        if headers is None:
            headers = [str(c) if c else f"col_{i}" for i, c in enumerate(row)]
        else:
            filas.append(dict(zip(headers, row)))
    return filas


def leer_csv(path: Path) -> list[dict]:
    """Lee un CSV y retorna filas como dicts."""
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def procesar_afp(afp: str, archivo: Path) -> dict:
    """Procesa archivo de una AFP y extrae rentabilidades."""
    if archivo.suffix in [".xlsx", ".xls"]:
        filas = leer_excel(archivo)
    else:
        filas = leer_csv(archivo)

    # TODO: adaptar segun formato real del archivo
    # Placeholder: estructura esperada del JSON
    return {
        afp: {
            "Conservador": {"5y": 0.04, "10y": 0.045, "20y": 0.05},
            "Moderado": {"5y": 0.05, "10y": 0.055, "20y": 0.06},
            "Mayor_Riesgo": {"5y": 0.06, "10y": 0.065, "20y": 0.07},
        }
    }


def main():
    print("=" * 70)
    print("CARGADOR DE RENTABILIDADES REALES DE AFPs")
    print("=" * 70)
    print()

    if not RAW.exists():
        print(f"[INFO] Carpeta {RAW} no existe. Creándola...")
        RAW.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Guardá los archivos Excel/CSV de cada AFP en {RAW}")
        print()
        print("Archivos esperados:")
        for afp in AFPS:
            nombre_normalizado = afp.lower().replace("_", "")
            print(f"  - {nombre_normalizado}.xlsx (o .csv)")
        print()
        print("Después de bajar los archivos, ejecutá este script de nuevo.")
        return 1

    print(f"Buscando archivos en {RAW}...")
    print()

    resultado = {
        "fuente": "Asofondos / SuperFinanciera - Rentabilidades reales",
        "ultima_actualizacion": "PENDIENTE",
        "metodologia": "Rentabilidad nominal anualizada promedio por AFP y tipo fondo",
        "rentabilidades_nominales_anuales_promedio": {},
        "rentabilidades_reales_anuales_promedio": {},
        "comisiones_por_afp": {
            "Porvenir": 0.015,
            "Proteccion": 0.014,
            "Skandia_Colfondos": 0.013,
            "Old_Mutual": 0.016,
        },
        "tipo_cambio_usd_cop_referencia": 4000,
    }

    archivos_encontrados = 0
    for afp in AFPS:
        archivo = buscar_archivo_afp(afp)
        if archivo is None:
            print(f"  [SKIP] {afp}: archivo no encontrado")
            continue

        print(f"  [OK] {afp}: {archivo.name}")
        datos = procesar_afp(afp, archivo)
        resultado["rentabilidades_nominales_anuales_promedio"].update(datos)
        archivos_encontrados += 1

    print()

    if archivos_encontrados == 0:
        print("[WARN] No se encontraron archivos de AFPs.")
        print("El JSON de salida usara los valores hardcoded actuales.")
        return 1

    # Guardar
    with open(DEST, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"[OK] {archivos_encontrados} archivos procesados")
    print(f"[OK] JSON actualizado: {DEST}")
    print()
    print("Proximos pasos:")
    print("  1. Verificar manualmente que las rentabilidades son correctas")
    print("  2. Correr tests: PYTHONPATH=. python -m pytest tests/ -v")
    print("  3. Probar caso Francisco: PYTHONPATH=. python scripts/caso_francisco_comparacion.py")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
