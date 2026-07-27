"""Tasas de cotización histórica a pensión en Colombia.

La tasa de cotización (porcentaje del salario que se aporta a pensión)
ha cambiado varias veces en Colombia. Este módulo documenta la
historia para entender cuánto se aportó en cada época.

NO afecta el cálculo del IBL (que usa el IBC reportado), pero SÍ
afecta cuánto dinero se acumuló en la cuenta individual.
"""
from datetime import date
from typing import Tuple


def tasa_cotizacion_vigente(fecha: date, ibc: float, smlmv: float = 1_600_000) -> float:
    """Devuelve la tasa total de cotización vigente en una fecha.

    Args:
        fecha: fecha del periodo cotizado
        ibc: ingreso base de cotización (mensual COP)
        smlmv: salario mínimo mensual legal vigente (default 2025 ≈ $1.600.000)

    Returns:
        Tasa total de cotización (decimal, ej 0.16 = 16%)

    HISTORIA:
        - Antes 2003:                6.5%  total
        - 2003-2016 (Ley 797):       7.125% total
        - 2016-2025 (Ley 1819):     progresivo 7.125% → 16%
        - Desde julio 2025:          16.0% total (12% emp + 4% trab)
                                    siempre que IBC > 4 SMLMV
    """
    # Implementación conservadora para MVP: usamos 16% desde 2025
    if fecha.year >= 2025:
        # Si gana más de 4 SMLMV, aplica 16% (Ley 2381/2024)
        if ibc > 4 * smlmv:
            return 0.16
        # Si gana menos, mantiene 8.5% (régimen especial)
        return 0.085

    if fecha.year >= 2017:
        # Período de transición Ley 1819/2016
        # Progresivo, simplificamos a un promedio
        if fecha.year == 2017: return 0.085
        if fecha.year == 2018: return 0.095
        if fecha.year == 2019: return 0.105
        if fecha.year == 2020: return 0.115
        if fecha.year == 2021: return 0.125
        if fecha.year == 2022: return 0.135
        if fecha.year == 2023: return 0.145
        if fecha.year == 2024: return 0.155
        return 0.16

    # Ley 797/2003 a 2016
    if fecha.year >= 2003:
        return 0.07125

    # Antes de 2003
    return 0.065


def aporte_mensual(ibc: float, fecha: date, smlmv: float = 1_600_000) -> float:
    """Calcula cuánto se aportó a pensión en un mes específico.

    Args:
        ibc: salario mensual
        fecha: fecha del periodo
        smlmv: salario mínimo vigente

    Returns:
        Monto en COP aportado a pensión ese mes
    """
    tasa = tasa_cotizacion_vigente(fecha, ibc, smlmv)
    return ibc * tasa


# === Ejemplo de uso ===
if __name__ == "__main__":
    # Francisco en 1984: ganaba $14.610
    aporte_1984 = aporte_mensual(14_610, date(1984, 8, 28))
    print(f"Aporte 1984 (${14_610}): ${aporte_1984:,.2f}")

    # Francisco en 2000: ganaba $389.200
    aporte_2000 = aporte_mensual(389_200, date(2000, 5, 1))
    print(f"Aporte 2000 (${389_200}): ${aporte_2000:,.2f}")

    # Francisco en 2025: gana $19.829.529
    aporte_2025 = aporte_mensual(19_829_529, date(2025, 7, 1))
    print(f"Aporte 2025 (${19_829_529}): ${aporte_2025:,.2f}")
