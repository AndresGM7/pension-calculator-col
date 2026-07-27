"""Modulo de legislacion colombiana sobre pensiones de vejez.

FUENTES DE LAS TASAS DE REEMPLAZO:

1. LEY 100/1993 (original) - Art. 34:
   - 1,000 semanas cotizadas: 65% del IBL
   - 1,000-1,200 semanas: 65% + 2% cada 50 semanas
   - 1,200-1,400 semanas: 73% + 3% cada 50 semanas
   - Maximo: 85% del IBL

2. LEY 797/2003 (Art. 10, modifica Art. 34) - Vigente actual:
   - Para quienes cumplan 1,300 semanas: 55% a 65% del IBL (decreciente segun ingreso)
   - Por cada 50 semanas adicionales sobre 1,300: +1.5% del IBL
   - Maximo: 80% del IBL
   - Minimo: 1 SMLMV (salario minimo legal vigente)

3. DECRETO 1158/2020 - Reglamenta Ley 797

4. LEY 2381/2024 (Reforma Petro):
   - Cambio en edad de jubilacion para mujeres
   - Pilar contributivo y solidario

NOTA SOBRE DECRECIENTE SEGUN INGRESO:
"el porcentaje disminuye progresivamente a medida que aumenta el nivel de ingresos del afiliado;
 a mayor ganancia (medida en salarios minimos), menor es la tasa de reemplazo inicial"
"""
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Literal


class RegimenPension(str, Enum):
    LEY_100_1993_ORIGINAL = "LEY_100_1993_ORIGINAL"
    LEY_797_2003_VIGENTE = "LEY_797_2003_VIGENTE"  # VIGENTE ACTUAL


@dataclass(frozen=True)
class ParametrosTasaReemplazo:
    """Parametros para calcular la tasa de reemplazo segun regimen legal."""
    regimen: RegimenPension
    semanas_minimas: int
    tasa_base_min: float  # Para menores ingresos
    tasa_base_max: float  # Para mayores ingresos
    incremento_por_50_semanas: float
    semanas_max_incremento: int
    tasa_maxima: float
    aplica_decreciente_por_ingreso: bool


# Parametros segun regimen
PARAMETROS_REGIMENES: dict[RegimenPension, ParametrosTasaReemplazo] = {
    RegimenPension.LEY_100_1993_ORIGINAL: ParametrosTasaReemplazo(
        regimen=RegimenPension.LEY_100_1993_ORIGINAL,
        semanas_minimas=1000,
        tasa_base_min=0.65,
        tasa_base_max=0.65,
        incremento_por_50_semanas=0.02,  # 2% cada 50 semanas
        semanas_max_incremento=1400,
        tasa_maxima=0.85,
        aplica_decreciente_por_ingreso=False,
    ),
    RegimenPension.LEY_797_2003_VIGENTE: ParametrosTasaReemplazo(
        regimen=RegimenPension.LEY_797_2003_VIGENTE,
        semanas_minimas=1300,
        tasa_base_min=0.55,  # 55% para altos ingresos
        tasa_base_max=0.65,  # 65% para bajos ingresos
        incremento_por_50_semanas=0.015,  # 1.5% cada 50 semanas
        semanas_max_incremento=1800,  # 50% adicional maximo
        tasa_maxima=0.80,
        aplica_decreciente_por_ingreso=True,
    ),
}


def calcular_tasa_ley_100_1993(semanas: int) -> float:
    """Tasa de reemplazo segun Ley 100/1993 ORIGINAL Art. 34.

    Formula: 65% a 1,000 semanas + 1.5% por cada 50 semanas adicionales.
    Maximo: 80%.
    """
    if semanas < 1000:
        return 0.0
    base = 0.65
    semanas_extra = max(0, semanas - 1000)
    incremento = (semanas_extra // 50) * 0.015
    return min(base + incremento, 0.80)


# Salarios minimos legales vigentes (referencia historica)
SMLMV_HISTORICO: dict[int, int] = {
    2020: 877_803,
    2021: 908_526,
    2022: 1_000_000,
    2023: 1_160_000,
    2024: 1_300_000,
    2025: 1_423_500,
    2026: 1_560_000,  # Estimado
}


def calcular_tasa_reemplazo_vigente(
    semanas_cotizadas: int,
    ibl_promedio: float,
    anio_calculo: int = 2026,
) -> float:
    """Calcula la tasa de reemplazo segun Ley 797/2003 vigente.

    Args:
        semanas_cotizadas: total de semanas cotizadas
        ibl_promedio: IBL promedio (ya indexado al IPC)
        anio_calculo: anio del calculo (para SMLMV)

    Returns:
        tasa de reemplazo (0.0 a 0.80)
    """
    params = PARAMETROS_REGIMENES[RegimenPension.LEY_797_2003_VIGENTE]

    if semanas_cotizadas < params.semanas_minimas:
        return 0.0

    # Determinar SMLMV del anio
    smlmv = SMLMV_HISTORICO.get(anio_calculo, 1_300_000)

    # Tasa base decreciente segun nivel de ingreso
    # Calcular ratio IBC/SMLMV
    ratio_ingreso = ibl_promedio / smlmv if smlmv > 0 else 1.0

    # Funcion decreciente: mas ingreso, menor tasa base
    # Para ratio <= 1 SMLMV: 65%
    # Para ratio = 4 SMLMV: 60%
    # Para ratio = 10 SMLMV: 55%
    if ratio_ingreso <= 1:
        tasa_base = params.tasa_base_max  # 65%
    elif ratio_ingreso <= 4:
        # Interpolar entre 65% y 60%
        proporcion = (ratio_ingreso - 1) / 3
        tasa_base = params.tasa_base_max - proporcion * 0.05
    elif ratio_ingreso <= 10:
        # Interpolar entre 60% y 55%
        proporcion = (ratio_ingreso - 4) / 6
        tasa_base = 0.60 - proporcion * 0.05
    else:
        tasa_base = params.tasa_base_min  # 55%

    # Incremento por semanas adicionales
    semanas_extra = max(0, semanas_cotizadas - params.semanas_minimas)
    incrementos = semanas_extra // 50
    tasa = tasa_base + (incrementos * params.incremento_por_50_semanas)

    # Tope maximo
    tasa = min(tasa, params.tasa_maxima)

    return tasa


# === Ejemplo ===
if __name__ == "__main__":
    # Francisco: 1,289 semanas, IBL ~17.6M
    ibl_francisco = 17_616_091
    print("=== Calculo de tasa de reemplazo (Ley 797/2003 vigente) ===")
    print(f"Para 1,289 semanas (NO califica):")
    tasa = calcular_tasa_reemplazo_vigente(1289, ibl_francisco)
    print(f"  Tasa: {tasa*100:.1f}%")
    print()
    print(f"Para 1,300 semanas (minimo):")
    tasa = calcular_tasa_reemplazo_vigente(1300, ibl_francisco)
    print(f"  Tasa: {tasa*100:.1f}% (sobre IBL de {ibl_francisco:,.0f})")
    print()
    print(f"Para 1,800 semanas (maximo):")
    tasa = calcular_tasa_reemplazo_vigente(1800, ibl_francisco)
    print(f"  Tasa: {tasa*100:.1f}%")
