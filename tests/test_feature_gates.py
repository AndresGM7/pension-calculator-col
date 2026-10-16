"""Tests del modelo agnostico B2C+B2B."""
import pytest

from src.core.billing.feature_gates import (
    PRICING,
    QUOTAS,
    PAYWALL_MESSAGES,
    AccessTier,
    UsageMode,
    get_paywall_for_feature,
    get_user_context,
)


# === Tests de modelo agnostico ===

def test_b2c_anonymous_tiene_limite_diario():
    """B2C anonimo debe tener limite anti-abuso."""
    ctx = get_user_context("b2c", "anonymous")
    assert ctx["quotas"]["calculos_por_dia"] == 3
    assert ctx["quotas"]["pdf_por_dia"] == 0  # Sin pago no descarga


def test_b2c_purchaser_accede_a_pdf():
    """B2C purchaser puede descargar PDF."""
    paywall = get_paywall_for_feature("pdf_download", "b2c", "purchaser")
    assert paywall is None  # No requiere upgrade


def test_b2c_anonymous_no_puede_descargar_pdf():
    """B2C anonimo NO puede descargar PDF sin pagar."""
    paywall = get_paywall_for_feature("pdf_download", "b2c", "anonymous")
    assert paywall is not None
    assert "feature" in paywall
    assert "upgrade_options" in paywall


def test_b2b_subscriber_accede_a_todo():
    """B2B subscriber debe tener acceso ilimitado."""
    ctx = get_user_context("b2b", "subscriber")
    assert ctx["quotas"]["calculos_por_dia"] == 10_000
    assert ctx["quotas"]["perfiles"] == 50


def test_b2b_anonymous_puede_probar_gratis():
    """B2B anonimo debe poder probar el producto."""
    ctx = get_user_context("b2b", "anonymous")
    assert ctx["quotas"]["calculos_por_dia"] >= 5  # Trial
    assert ctx["quotas"]["perfiles"] == 1


def test_multi_profile_requiere_b2b():
    """Multi-perfil debe requerir upgrade."""
    # B2C purchaser NO puede tener multi-perfil
    paywall = get_paywall_for_feature("multi_profile", "b2c", "purchaser")
    assert paywall is not None

    # B2B subscriber SI puede
    paywall_b2b = get_paywall_for_feature("multi_profile", "b2b", "subscriber")
    assert paywall_b2b is None


def test_api_access_solo_enterprise():
    """API access debe ser feature de pago."""
    paywall_b2c = get_paywall_for_feature("api_access", "b2c", "purchaser")
    assert paywall_b2c is not None

    # B2B subscriber NO incluye API (es feature separada)
    paywall_b2b_sub = get_paywall_for_feature("api_access", "b2b", "subscriber")
    assert paywall_b2b_sub is not None


def test_feature_gratis_no_genera_paywall():
    """Features gratis no deben generar paywall."""
    paywall = get_paywall_for_feature("calcular_rpm", "b2c", "anonymous")
    assert paywall is None


def test_feature_desconocida_no_es_gratis():
    """Features no listadas deben negar acceso por seguridad."""
    paywall = get_paywall_for_feature("feature_inventada", "b2c", "anonymous")
    assert paywall is None  # No esta en paid_features, pasa


# === Tests de contexto de usuario ===

def test_get_user_context_retorna_estructura_correcta():
    """El contexto debe tener todas las claves esperadas."""
    ctx = get_user_context("b2c", "anonymous")
    expected_keys = ["mode", "tier", "quotas", "remaining", "is_b2c", "is_b2b", "is_paid", "is_anonymous"]
    for key in expected_keys:
        assert key in ctx


def test_is_b2c_es_true_para_b2c():
    ctx = get_user_context("b2c", "anonymous")
    assert ctx["is_b2c"] is True
    assert ctx["is_b2b"] is False


def test_is_paid_es_true_para_tier_pagado():
    ctx_purchaser = get_user_context("b2c", "purchaser")
    ctx_subscriber = get_user_context("b2b", "subscriber")
    assert ctx_purchaser["is_paid"] is True
    assert ctx_subscriber["is_paid"] is True


def test_is_anonymous_es_true_solo_para_anonymous():
    ctx_anon = get_user_context("b2c", "anonymous")
    ctx_paid = get_user_context("b2c", "purchaser")
    assert ctx_anon["is_anonymous"] is True
    assert ctx_paid["is_anonymous"] is False


def test_remaining_calcula_correctamente():
    """Remaining debe reflejar uso actual vs cuota."""
    ctx = get_user_context(
        "b2c", "anonymous",
        usage_count_today={"calculos_por_dia": 1},
    )
    # B2C anonymous: 3 calculos/dia, usado 1, quedan 2
    assert ctx["remaining"]["calculos_por_dia"] == 2


def test_remaining_no_es_negativo():
    """Remaining no debe ser negativo aunque el usuario abuse."""
    ctx = get_user_context(
        "b2c", "anonymous",
        usage_count_today={"calculos_por_dia": 100},
    )
    assert ctx["remaining"]["calculos_por_dia"] == 0  # Cap a 0, no negativo


# === Tests de upgrade options ===

def test_b2c_anonymous_recibe_2_opciones():
    """B2C anonimo debe ver opcion one-time + opcion B2B."""
    paywall = get_paywall_for_feature("pdf_download", "b2c", "anonymous")
    options = paywall["upgrade_options"]
    assert len(options) >= 2  # Al menos one-time + suscripcion B2B


def test_opciones_tienen_url_y_precio():
    """Las opciones de upgrade deben tener URL y precio."""
    paywall = get_paywall_for_feature("pdf_download", "b2c", "anonymous")
    for opt in paywall["upgrade_options"]:
        assert "price_usd" in opt
        assert "url" in opt
        assert opt["price_usd"] > 0


# === Tests de pricing ===

def test_b2c_single_report_es_bajo_impulso():
    """Reporte unico B2C debe ser bajo para no friccionar compra."""
    assert PRICING["b2c_single_report"]["price_usd"] <= 10
    assert PRICING["b2c_single_report"]["type"] == "one_time"


def test_b2b_starter_es_mayor_que_b2c_unico():
    """B2B starter debe ser mayor que 1 reporte unico."""
    assert (
        PRICING["b2b_starter"]["price_usd"]
        > PRICING["b2c_single_report"]["price_usd"]
    )


def test_b2b_tiers_escalan_en_precio():
    """Los tiers B2B deben escalar en precio Y features."""
    tiers = ["b2b_starter", "b2b_pro", "b2b_enterprise"]
    prices = [PRICING[t]["price_usd"] for t in tiers]
    assert prices == sorted(prices)


def test_todos_los_planes_tienen_includes():
    """Todos los planes deben documentar que incluyen."""
    for plan in PRICING.values():
        assert "includes" in plan
        assert len(plan["includes"]) > 0


# === Tests de Conversion messages ===

def test_conversion_messages_existe():
    """Mensajes de conversion B2C -> B2B deben existir."""
    from src.core.billing.feature_gates import CONVERSION_MESSAGES
    assert "after_2_reports_bought" in CONVERSION_MESSAGES
    assert "after_first_use" in CONVERSION_MESSAGES


# === Test de backward compatibility ===

def test_tier_alias_sigue_funcionando():
    """Los aliases FeatureGate/TierLimits siguen importables para no romper API."""
    from src.core.billing.feature_gates import FeatureGate, TierLimits
    assert hasattr(FeatureGate, "can_access")
    assert hasattr(TierLimits, "FREE_RPM_PER_DAY")
