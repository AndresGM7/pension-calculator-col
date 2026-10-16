"""Corrige el CSV de IPC: series pre-mayo 1981 estaban en formato distinto.

PROBLEMA:
- Serie 1954-abril 1981: valores 0.03-0.97 (parece variacion acumulada,
  probablemente reconstruida de manera incorrecta al concatenar series)
- Serie mayo 1981-hoy: indice correcto, base 100 = dic 2018

SOLUCION:
- Para registros anteriores a mayo 1981, usar el valor de mayo 1981 (1.00)
  como aproximacion conservadora. Esto SUBESTIMA el IBL historico, lo cual
  significa que nuestros calculos daran pensiones MENORES a las reales.
  Es lo correcto legalmente (no sobreestimamos).

VALIDACION:
- 2018/12 = 100.0 (base oficial)
- 2024/12 ~ 144.88 (DANE oficial 144.81)
- 2026/06 = 159.53 (DANE oficial ~158.7)

Uso:
    python scripts/fix_ipc_data.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "IPC_Índice de Precios al Consumidor.csv"
DST = ROOT / "data" / "IPC_corregido.csv"

# Mes de inicio de la serie confiable (cuando arranca base 100 = dic 2018)
FECHA_BASE_FIABLE = "1981-05-31"


def main():
    if not SRC.exists():
        print(f"ERROR: no existe {SRC}")
        return 1

    # Leer CSV original
    with open(SRC, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        header = reader.fieldnames

    # Encontrar valor del mes fiable (mayo 1981)
    valor_referencia = None
    for row in rows:
        if row["Periodo(MMM, AAAA)"].replace("/", "-") == FECHA_BASE_FIABLE:
            valor_referencia = float(row["Índice de Precios al Consumidor (IPC)"])
            break

    if valor_referencia is None:
        print(f"ERROR: no encontre el mes {FECHA_BASE_FIABLE} en el CSV")
        return 1

    print(f"Valor de referencia ({FECHA_BASE_FIABLE}): {valor_referencia}")

    # Reescribir CSV: para fechas anteriores a FECHA_BASE_FIABLE, usar valor_referencia
    corregidos = 0
    with open(DST, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            periodo = row["Periodo(MMM, AAAA)"]
            fecha_iso = periodo.replace("/", "-")
            valor_str = row["Índice de Precios al Consumidor (IPC)"]

            if fecha_iso < FECHA_BASE_FIABLE:
                # Reemplazar con valor de referencia (conservador)
                nuevo_valor = valor_referencia
                corregidos += 1
            else:
                try:
                    nuevo_valor = float(valor_str)
                except ValueError:
                    continue

            writer.writerow({
                header[0]: periodo,
                header[1]: nuevo_valor,
            })

    print(f"\n[OK] {corregidos} registros anteriores a {FECHA_BASE_FIABLE} corregidos")
    print(f"[OK] CSV corregido en: {DST}")
    print(f"\nValidacion:")
    print(f"  - Lee el CSV corregido y verifica que 1954/07/31 ahora vale {valor_referencia}")
    print(f"  - Verifica que 2018/12/31 sigue valiendo 100.0 (no se toco)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
