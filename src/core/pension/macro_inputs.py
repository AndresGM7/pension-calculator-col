"""Carga inputs macroeconomicos para proyecciones (inflacion, SMLMV, IBC).

FUENTES DE DATOS OFICIALES (Sep 2026):
- SMLMV historico: Banrep (https://suameca.banrep.gov.co/graficador-interactivo/grafica/15416)
  Datos: data/macro_proyecciones.json -> smlmv_historico_anual_cop
- Expectativas de inflacion: Banrep (https://suameca.banrep.gov.co/estadisticas-economicas/encuestas)
  Datos: data/macro_proyecciones.json -> expectativas_inflacion_historicas_banrep
- IPC historico: DANE (https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/ipc)
  Datos: data/macro_proyecciones.json -> ipc_historico_anual_oficial
- Rentabilidades AFP: Colfondos/SuperFinanciera (Carta Circular 39/2026)
  Datos: data/rais_rentabilidades.json
- IBC medio: DANE GEIH

Para ACTUALIZAR datos en el futuro:
1. Bajar chart.csv de Banrep -> pegar en Downloads
2. Bajar series_historicas.xlsx de Banrep -> pegar en Downloads
3. Correr python scripts/actualizar_datos_oficiales.py
"""
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_FILE = ROOT / "data" / "macro_proyecciones.json"
RAIS_FILE = ROOT / "data" / "rais_rentabilidades.json"


def cargar_macro() -> dict:
    """Carga el JSON de proyecciones macro."""
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_rentabilidades_rais() -> dict:
    """Carga el JSON de rentabilidades RAIS."""
    if not RAIS_FILE.exists():
        return {}
    with open(RAIS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def obtener_inflacion_proyectada(
    anio: int,
    escenario: str = "Base",
) -> float | None:
    """Obtiene la inflacion proyectada para un anio especifico y escenario.

    Args:
        anio: Anio de la proyeccion (ej. 2030)
        escenario: "Conservador", "Base" o "Agresivo"

    Returns:
        Tasa de inflacion proyectada (0.05 = 5%) o None si no esta disponible
    """
    data = cargar_macro()
    return (
        data.get("escenarios_inflacion_proyectada", {})
        .get(escenario, {})
        .get(str(anio))
    )


def obtener_smlmv_historico(anio: int) -> int | None:
    """Obtiene el SMLMV anual historico (oficial Banrep)."""
    data = cargar_macro()
    return data.get("smlmv_historico_anual_cop", {}).get(str(anio))


def obtener_ipc_historico(anio: int) -> float | None:
    """Obtiene el IPC anual historico (oficial)."""
    data = cargar_macro()
    return data.get("ipc_historico_anual_oficial", {}).get(str(anio))


def obtener_expectativas_inflacion_banrep() -> dict:
    """Retorna las expectativas de inflacion promedio anuales del Banrep."""
    data = cargar_macro()
    return data.get("expectativas_inflacion_historicas_banrep", {})


def obtener_ultimo_dato_esperado_inflacion() -> dict:
    """Retorna el ultimo dato de expectativas de inflacion del Banrep."""
    data = cargar_macro()
    return data.get("expectativas_inflacion_historicas_banrep", {}).get("ultimo_dato_sep_2026", {})


def obtener_smlmv_proyectado(
    anio: int,
    escenario: str = "Base",
) -> int | None:
    """Obtiene el SMLMV proyectado para un anio especifico y escenario.

    NOTA: No hay proyecciones oficiales del SMLMV. Se estiman aplicando
    crecimiento nominal = inflacion escenario + crecimiento real escenario
    al ultimo SMLMV conocido.
    """
    smlmv_actual = obtener_smlmv_historico(2026)
    if not smlmv_actual:
        return None

    inflacion = obtener_inflacion_proyectada(anio, escenario)
    crecimiento_real = obtener_crecimiento_salarial_real(escenario)

    if inflacion is None or anio <= 2026:
        return None

    anios_desde_hoy = anio - 2026
    factor_total = (1 + inflacion + crecimiento_real) ** anios_desde_hoy
    return int(smlmv_actual * factor_total)


def obtener_crecimiento_salarial_real(escenario: str = "Base") -> float:
    """Obtiene la tasa de crecimiento salarial real esperada por escenario."""
    data = cargar_macro()
    return data.get("crecimiento_salarial_real_anual", {}).get(escenario, 0.015)


def obtener_rentabilidad_afp(
    afp: str,
    tipo_fondo: str,
    plazo: str = "5y",
) -> float | None:
    """Obtiene la rentabilidad nominal anual de una AFP especifica.

    Args:
        afp: "Porvenir", "Proteccion", "Skandia_Colfondos", "Old_Mutual"
        tipo_fondo: "Conservador", "Moderado", "Mayor_Riesgo"
        plazo: "3y", "5y", "10y", "largo_plazo"

    Returns:
        Rentabilidad nominal anual (0.11 = 11%) o None si no esta disponible
    """
    data = cargar_rentabilidades_rais()
    return (
        data.get("rentabilidades_nominales_anuales_promedio", {})
        .get(afp, {})
        .get(tipo_fondo, {})
        .get(plazo)
    )


def obtener_rentabilidad_promedio_sector(
    tipo_fondo: str,
    plazo: str = "5y",
) -> float:
    """Obtiene la rentabilidad promedio del sector (todas las AFPs) para un fondo."""
    afps = ["Porvenir", "Proteccion", "Skandia_Colfondos", "Old_Mutual"]
    rentabilidades = []

    for afp in afps:
        r = obtener_rentabilidad_afp(afp, tipo_fondo, plazo)
        if r is not None:
            rentabilidades.append(r)

    if not rentabilidades:
        return 0.05  # fallback conservador

    return sum(rentabilidades) / len(rentabilidades)


def obtener_rentabilidad_minima_obligatoria(tipo_fondo: str, periodo: str = "3y") -> float | None:
    """Obtiene la rentabilidad minima obligatoria segun Carta Circular 39/2026."""
    data = cargar_rentabilidades_rais()
    tir_data = data.get("rentabilidades_acumuladas_efectivas_anuales_tir", {})

    key_map = {
        ("Conservador", "3y"): "periodo_3y_jun2023_jun2026",
        ("Mayor_Riesgo", "5y"): "periodo_5y_jun2021_jun2026",
        ("Moderado", "4y"): "periodo_4y_moderado_jun2022_jun2026",
    }

    key = key_map.get((tipo_fondo, periodo))
    if key and key in tir_data:
        return tir_data[key].get("rentabilidad_minima_obligatoria")

    return None


def proyectar_ibc_futuro(
    ibc_actual: float,
    anios: int,
    inflacion_anual: float,
    crecimiento_real_anual: float,
) -> float:
    """Proyecta el IBC futuro aplicando inflacion + crecimiento real."""
    factor_total = (1 + inflacion_anual + crecimiento_real_anual) ** anios
    return ibc_actual * factor_total


def obtener_topes_legales() -> dict:
    """Obtiene los topes legales aplicables al calculo de pension."""
    data = cargar_macro()
    return data.get("topes_legales_para_pension", {
        "smlmv": 1,
        "tope_maximo_ibc_en_smlmv": 25,
        "tope_ib_en_uvt_anual_para_indemnizacion_sustitutiva": 300,
    })


def validar_ibc_contra_topes(ibc: float, smlmv_actual: int) -> dict:
    """Valida si un IBC esta dentro de los rangos legales."""
    topes = obtener_topes_legales()
    tope_minimo = smlmv_actual * topes["smlmv"]
    tope_maximo = smlmv_actual * topes["tope_maximo_ibc_en_smlmv"]

    if ibc < tope_minimo:
        ibl_normalizado = tope_minimo
    elif ibc > tope_maximo:
        ibl_normalizado = tope_maximo
    else:
        ibl_normalizado = ibc

    return {
        "dentro_de_topes": tope_minimo <= ibc <= tope_maximo,
        "tope_minimo": tope_minimo,
        "tope_maximo": tope_maximo,
        "ibl_normalizado": ibl_normalizado,
    }


def resumen_macro_actual() -> dict:
    """Retorna resumen de los inputs macro actuales del sistema."""
    data = cargar_macro()
    ultimas_exp = data.get("expectativas_inflacion_historicas_banrep", {}).get("ultimo_dato_sep_2026", {})

    return {
        "ultima_actualizacion": data.get("ultima_actualizacion"),
        "smlmv_actual_cop": data.get("smlmv_historico_anual_cop", {}).get("2026"),
        "expectativas_inflacion_12m_actual": ultimas_exp.get("inflacion_12m_promedio"),
        "expectativas_inflacion_24m_actual": ultimas_exp.get("inflacion_24m_promedio"),
        "expectativas_inflacion_60m_actual": ultimas_exp.get("inflacion_60m_promedio"),
        "ipc_oficial_2025": data.get("ipc_historico_anual_oficial", {}).get("2025"),
        "ipc_oficial_2026_estimado": data.get("ipc_historico_anual_oficial", {}).get("2026_estimado"),
        "smlmv_proyeccion_5y_conservador": obtener_smlmv_proyectado(2031, "Conservador"),
        "smlmv_proyeccion_5y_base": obtener_smlmv_proyectado(2031, "Base"),
        "smlmv_proyeccion_5y_agresivo": obtener_smlmv_proyectado(2031, "Agresivo"),
    }


def listar_fuentes_oficiales() -> list[dict]:
    """Lista todas las fuentes oficiales y URLs para reproducibilidad."""
    data = cargar_macro()
    fuentes = data.get("fuentes_oficiales_reproducibles", {})
    return [{"nombre": k, "url": v} for k, v in fuentes.items()]