"""Tests del modulo de inputs macroeconomicos.

Datos verificados contra:
- Banrep chart.csv (SMLMV 1984-2026)
- Banrep series_historicas.xlsx (expectativas inflacion 2003-2026)
- Colfondos / SuperFinanciera (Carta Circular 39/2026)
"""
from src.core.pension.macro_inputs import (
    cargar_macro,
    cargar_rentabilidades_rais,
    listar_fuentes_oficiales,
    obtener_crecimiento_salarial_real,
    obtener_expectativas_inflacion_banrep,
    obtener_inflacion_proyectada,
    obtener_ipc_historico,
    obtener_rentabilidad_afp,
    obtener_rentabilidad_minima_obligatoria,
    obtener_rentabilidad_promedio_sector,
    obtener_smlmv_historico,
    obtener_smlmv_proyectado,
    obtener_topes_legales,
    obtener_ultimo_dato_esperado_inflacion,
    proyectar_ibc_futuro,
    resumen_macro_actual,
    validar_ibc_contra_topes,
)


def test_cargar_macro_retorna_dict():
    data = cargar_macro()
    assert isinstance(data, dict)
    assert "smlmv_historico_anual_cop" in data


def test_cargar_rentabilidades_rais_retorna_dict():
    data = cargar_rentabilidades_rais()
    assert isinstance(data, dict)
    assert "rentabilidades_acumuladas_efectivas_anuales_tir" in data


def test_obtener_smlmv_historico_oficial_banrep():
    """SMLMV 2024 oficial Banrep = 1.300.000 COP"""
    smlmv_2024 = obtener_smlmv_historico(2024)
    assert smlmv_2024 == 1_300_000


def test_obtener_smlmv_historico_desde_1984():
    """SMLMV 1984 = 11.298 COP (primer valor oficial)"""
    smlmv_1984 = obtener_smlmv_historico(1984)
    assert smlmv_1984 == 11_298


def test_obtener_smlmv_historico_anio_inexistente():
    assert obtener_smlmv_historico(1900) is None


def test_obtener_smlmv_historico_43_anios_disponibles():
    """SMLMV oficial disponible 1984-2026 (43 anos)."""
    data = cargar_macro()
    smlmv = data.get("smlmv_historico_anual_cop", {})
    # Excluir entradas que empiezan con _
    anios = [int(k) for k in smlmv.keys() if not k.startswith("_") and k.isdigit()]
    assert len(anios) == 43
    assert min(anios) == 1984
    assert max(anios) == 2026


def test_obtener_inflacion_proyectada_escenarios():
    """Los 3 escenarios deben estar definidos y respetar el orden."""
    inflacion_2030_base = obtener_inflacion_proyectada(2030, "Base")
    inflacion_2030_agresivo = obtener_inflacion_proyectada(2030, "Agresivo")
    inflacion_2030_conservador = obtener_inflacion_proyectada(2030, "Conservador")

    # Agresivo < Base < Conservador
    assert inflacion_2030_agresivo < inflacion_2030_base < inflacion_2030_conservador


def test_obtener_inflacion_proyectada_fuera_de_rango():
    assert obtener_inflacion_proyectada(2050, "Base") is None


def test_obtener_ipc_historico_anios_recientes():
    assert obtener_ipc_historico(2024) == 0.0522
    assert obtener_ipc_historico(2025) == 0.0493


def test_obtener_expectativas_inflacion_banrep_estructura():
    exp = obtener_expectativas_inflacion_banrep()
    assert "promedio_anual_inflacion_12m" in exp
    assert "ultimo_dato_sep_2026" in exp


def test_obtener_ultimo_dato_esperado_inflacion():
    """El ultimo dato de Banrep (Sep 2026) debe estar disponible."""
    ultimo = obtener_ultimo_dato_esperado_inflacion()
    assert ultimo["inflacion_12m_promedio"] > 0
    assert ultimo["inflacion_12m_promedio"] < 0.15  # sanity check


def test_obtener_smlmv_proyectado_crece_con_anios():
    smlmv_2027 = obtener_smlmv_proyectado(2027, "Base")
    smlmv_2035 = obtener_smlmv_proyectado(2035, "Base")
    assert smlmv_2035 > smlmv_2027


def test_obtener_smlmv_proyectado_anio_pasado_none():
    assert obtener_smlmv_proyectado(2020, "Base") is None


def test_crecimiento_salarial_real_positivo():
    for escenario in ["Conservador", "Base", "Agresivo"]:
        crecimiento = obtener_crecimiento_salarial_real(escenario)
        assert crecimiento >= 0


def test_proyectar_ibc_futuro_crecimiento_compuesto():
    ibc_actual = 5_000_000
    ibc_5y = proyectar_ibc_futuro(
        ibc_actual=ibc_actual,
        anios=5,
        inflacion_anual=0.05,
        crecimiento_real_anual=0.02,
    )
    assert ibc_5y > ibc_actual * 1.30
    assert ibc_5y < ibc_actual * 1.50


def test_proyectar_ibc_sin_inflacion_solo_real():
    ibc = proyectar_ibc_futuro(
        ibc_actual=1_000_000,
        anios=10,
        inflacion_anual=0,
        crecimiento_real_anual=0.02,
    )
    assert abs(ibc - 1_219_000) < 1000


def test_obtener_topes_legales_estructura():
    topes = obtener_topes_legales()
    assert topes["smlmv"] == 1
    assert topes["tope_maximo_ibc_en_smlmv"] == 25


def test_validar_ibc_por_debajo_del_minimo():
    smlmv_2026 = 1_560_000
    ibc_bajo = smlmv_2026 * 0.5
    resultado = validar_ibc_contra_topes(ibc_bajo, smlmv_2026)
    assert resultado["dentro_de_topes"] is False
    assert resultado["ibl_normalizado"] == smlmv_2026


def test_validar_ibc_dentro_del_rango():
    smlmv_2026 = 1_560_000
    ibc_normal = smlmv_2026 * 5
    resultado = validar_ibc_contra_topes(ibc_normal, smlmv_2026)
    assert resultado["dentro_de_topes"] is True
    assert resultado["ibl_normalizado"] == ibc_normal


def test_validar_ibc_por_encima_del_tope():
    smlmv_2026 = 1_560_000
    ibc_alto = smlmv_2026 * 30
    resultado = validar_ibc_contra_topes(ibc_alto, smlmv_2026)
    assert resultado["dentro_de_topes"] is False
    assert resultado["ibl_normalizado"] == smlmv_2026 * 25


def test_obtener_rentabilidad_afp_porvenir_5y():
    """Rentabilidad nominal anual promedio Porvenir 5y segun Carta Circular 39/2026."""
    r = obtener_rentabilidad_afp("Porvenir", "Conservador", "5y")
    assert r is not None
    assert 0.05 < r < 0.15  # Entre 5% y 15%


def test_obtener_rentabilidad_afp_skancia_colfondos_10y():
    r = obtener_rentabilidad_afp("Skandia_Colfondos", "Mayor_Riesgo", "10y")
    assert r is not None


def test_obtener_rentabilidad_promedio_sector_moderado():
    r = obtener_rentabilidad_promedio_sector("Moderado", "5y")
    assert r > 0
    assert r < 0.20


def test_obtener_rentabilidad_minima_obligatoria_conservador():
    """Rentabilidad minima obligatoria Conservador periodo 3y = 7.47%"""
    r = obtener_rentabilidad_minima_obligatoria("Conservador", "3y")
    assert r == 0.0747


def test_obtener_rentabilidad_minima_obligatoria_moderado():
    """Rentabilidad minima obligatoria Moderado periodo 4y = 7.89%"""
    r = obtener_rentabilidad_minima_obligatoria("Moderado", "4y")
    assert r == 0.0789


def test_resumen_macro_actual_tiene_keys():
    resumen = resumen_macro_actual()
    assert "smlmv_actual_cop" in resumen
    assert "expectativas_inflacion_12m_actual" in resumen
    assert resumen["smlmv_actual_cop"] > 1_000_000


def test_listar_fuentes_oficiales_retorna_lista():
    fuentes = listar_fuentes_oficiales()
    assert isinstance(fuentes, list)
    assert len(fuentes) > 5  # varias fuentes oficiales
    # Verificar que las URLs son validas
    fuentes_con_url = [f for f in fuentes if f["url"].startswith("http")]
    assert len(fuentes_con_url) >= 5  # al menos 5 URLs reales
    for fuente in fuentes:
        assert "nombre" in fuente
        assert "url" in fuente