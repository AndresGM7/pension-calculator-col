"""Modelo agnostico B2C+B2B para pension-calculator.

ARQUITECTURA:
- NO usamos tiers verticales (free/premium/pro) con feature gates.
- En su lugar: el mismo motor sirve para B2C y B2B.
- El "modo de uso" se autodetecta:
  - B2C: usuario individual paga por reporte unico ($5)
  - B2B: contador paga suscripcion mensual, tiene N perfiles

FEATURES (sin gates verticales, todas disponibles segun el contexto):
- Cualquier usuario puede usar el motor completo (calcular RPM, RAIS, comparar)
- Las features que requieren pago son: descargar PDF, guardar perfiles, alertas
- B2B tiene CUOTAS (perfiles permitidos por mes) vs B2C con pago unico

Por que este modelo:
- Mas etico: el usuario B2C no encuentra paywalls duros
- Mas simple: una sola pieza de codigo, dos canales de monetizacion
- Mas flexible: el mismo reporte vale para B2C o lo reusa el contador B2B
"""
from enum import Enum
from typing import Literal


USAGE_MODE = Literal["b2c", "b2b"]
ACCESS_TIER = Literal["anonymous", "purchaser", "subscriber"]


class UsageMode:
    """Define el modo de uso del producto."""

    B2C = "b2c"      # Usuario individual, paga por reporte unico
    B2B = "b2b"      # Contador/empresa, paga suscripcion mensual


class AccessTier:
    """Define el nivel de acceso del usuario (basado en compras/suscripciones)."""

    ANONYMOUS = "anonymous"     # Sin pago
    PURCHASER = "purchaser"     # Compro 1+ reportes B2C
    SUBSCRIBER = "subscriber"   # Suscripcion B2B activa


# === Cuotas y limites por modo ===

QUOTAS = {
    # B2C Anonymous: 3 calculos/dia (anti-abuso)
    ("b2c", "anonymous"): {
        "calculos_por_dia": 3,
        "pdf_por_dia": 0,           # No descarga PDF sin pagar
        "perfiles": 1,
        "comparaciones_por_dia": 0,  # Solo RPM basico sin pagar
        "proyecciones_por_dia": 0,
    },
    # B2C Purchaser: compro al menos 1 reporte
    ("b2c", "purchaser"): {
        "calculos_por_dia": 100,
        "pdf_por_dia": 50,
        "perfiles": 1,
        "comparaciones_por_dia": 50,
        "proyecciones_por_dia": 50,
    },
    # B2B Anonymous: puede probar 1 vez antes de subscribirse
    ("b2b", "anonymous"): {
        "calculos_por_dia": 10,
        "pdf_por_dia": 1,
        "perfiles": 1,
        "comparaciones_por_dia": 5,
        "proyecciones_por_dia": 5,
    },
    # B2B Subscriber: contador con suscripcion activa
    ("b2b", "subscriber"): {
        "calculos_por_dia": 10_000,  # Practicamente ilimitado
        "pdf_por_dia": 10_000,
        "perfiles": 50,
        "comparaciones_por_dia": 10_000,
        "proyecciones_por_dia": 10_000,
    },
}


# === Precios ===

PRICING = {
    # Reporte unico B2C: bajo para no friccionar, pero con upgrade a suscripcion
    "b2c_single_report": {
        "price_usd": 5,
        "price_cop": 20_000,
        "type": "one_time",
        "includes": "Reporte completo PDF + 30 dias de acceso a calculos ilimitados",
        "renewal": "manual",
    },
    # Suscripcion B2B contador: tier basico
    "b2b_starter": {
        "price_usd": 29,
        "price_cop": 120_000,
        "type": "recurring_monthly",
        "includes": "5 perfiles de clientes + reportes ilimitados",
        "renewal": "automatic",
    },
    # Suscripcion B2B contador: tier pro
    "b2b_pro": {
        "price_usd": 99,
        "price_cop": 400_000,
        "type": "recurring_monthly",
        "includes": "50 perfiles + export Excel + alertas normativas",
        "renewal": "automatic",
    },
    # B2B Enterprise: para firmas grandes
    "b2b_enterprise": {
        "price_usd": 249,
        "price_cop": 1_000_000,
        "type": "recurring_monthly",
        "includes": "Perfiles ilimitados + API access + soporte dedicado",
        "renewal": "automatic",
    },
}


# === Mensajes de paywall (NO gates duros, siempre descriptivos) ===

PAYWALL_MESSAGES = {
    "pdf_required": {
        "b2c": "Descarga tu reporte en PDF por $5 USD unico. Sin suscripcion, sin permanencia.",
        "b2b": "Descarga el reporte para tu cliente. Tu suscripcion B2B cubre esto.",
    },
    "multi_profile_required": {
        "b2c": "En modo B2C solo podes guardar 1 perfil. Para multiples perfiles (familia), considerá el modo B2B desde $29/mes.",
        "b2b": "Tu plan B2B te permite gestionar multiples perfiles de clientes.",
    },
    "alertas_required": {
        "b2c": "Las alertas normativas son una feature B2B Pro ($99/mes). Sirven para que tu contador te avise de cambios.",
        "b2b": "Feature disponible en plan B2B Pro ($99/mes).",
    },
    "api_required": {
        "b2c": "API solo en plan B2B Enterprise ($249/mes).",
        "b2b": "API disponible en plan B2B Enterprise ($249/mes). Si necesitas mas volumen, contactanos.",
    },
}


def get_user_context(
    mode: str,
    tier: str,
    usage_count_today: dict = None,
) -> dict:
    """Retorna el contexto completo del usuario (modo + tier + cuotas).

    Args:
        mode: "b2c" o "b2b"
        tier: "anonymous", "purchaser" o "subscriber"
        usage_count_today: dict con contadores de uso del dia

    Returns:
        dict con contexto completo del usuario
    """
    if usage_count_today is None:
        usage_count_today = {}

    quotas = QUOTAS.get((mode, tier), QUOTAS[("b2c", "anonymous")])

    # Calcular uso restante
    remaining = {}
    for key, limit in quotas.items():
        used = usage_count_today.get(key, 0)
        if limit == float("inf"):
            remaining[key] = float("inf")
        else:
            remaining[key] = max(0, limit - used)

    return {
        "mode": mode,
        "tier": tier,
        "quotas": quotas,
        "remaining": remaining,
        "is_b2c": mode == "b2c",
        "is_b2b": mode == "b2b",
        "is_paid": tier in ("purchaser", "subscriber"),
        "is_anonymous": tier == "anonymous",
    }


def get_paywall_for_feature(
    feature: str,
    mode: str,
    tier: str,
) -> dict | None:
    """Retorna mensaje de paywall si la feature requiere upgrade.

    Returns:
        None si la feature es accesible
        dict con info de upgrade si requiere pago
    """
    # Features que requieren pago especifico
    paid_features = {
        "pdf_download": "pdf_required",
        "multi_profile": "multi_profile_required",
        "alertas_normativas": "alertas_required",
        "api_access": "api_required",
    }

    msg_key = paid_features.get(feature)
    if msg_key is None:
        return None  # Feature gratis para todos

    # B2C purchaser ya pago, tiene acceso a PDF
    if mode == "b2c" and tier == "purchaser" and feature == "pdf_download":
        return None

    # B2B subscriber tiene acceso a multi_profile y alertas
    # pero NO a api_access (eso es Enterprise)
    if mode == "b2b" and tier == "subscriber" and feature in ("multi_profile", "alertas_normativas"):
        return None

    # API access requiere Enterprise (no incluido en subscriber basico)
    # Para B2B, "subscriber" es starter/pro pero no enterprise
    # Esto se verifica en otro lado con el plan especifico

    message = PAYWALL_MESSAGES[msg_key]
    return {
        "feature": feature,
        "mode": mode,
        "tier": tier,
        "message": message.get(mode, message.get("b2c")),
        "upgrade_options": _get_upgrade_options(mode, tier),
    }


def _get_upgrade_options(mode: str, tier: str) -> list[dict]:
    """Retorna opciones de upgrade segun el modo/tier actual."""
    if mode == "b2c" and tier == "anonymous":
        # B2C anonimo: sugerir compra unica O cambiar a B2B
        return [
            {
                "type": "one_time",
                "name": "Reporte unico",
                "price_usd": PRICING["b2c_single_report"]["price_usd"],
                "url": "/checkout/reporte-unico",
                "for": "Si queres solo un reporte de tu pension",
            },
            {
                "type": "subscription",
                "name": "Plan B2B Starter",
                "price_usd": PRICING["b2b_starter"]["price_usd"],
                "url": "/checkout/b2b-starter",
                "for": "Si sos contador o asesor con multiples clientes",
            },
        ]
    elif mode == "b2c" and tier == "purchaser":
        # Ya es purchaser, ofrecer upgrade a B2B para mas perfiles
        return [
            {
                "type": "subscription",
                "name": "Plan B2B Starter",
                "price_usd": PRICING["b2b_starter"]["price_usd"],
                "url": "/checkout/b2b-starter",
                "for": "Para multiples perfiles o uso continuo",
            },
        ]
    elif mode == "b2b" and tier == "anonymous":
        # B2B anonimo: ofrecer suscripcion
        return [
            {
                "type": "subscription",
                "name": "Plan B2B Starter",
                "price_usd": PRICING["b2b_starter"]["price_usd"],
                "url": "/checkout/b2b-starter",
                "for": "Para contadores pequenos",
            },
            {
                "type": "subscription",
                "name": "Plan B2B Pro",
                "price_usd": PRICING["b2b_pro"]["price_usd"],
                "url": "/checkout/b2b-pro",
                "for": "Para contadores con muchos clientes",
            },
        ]
    return []


# === Conversion messages (B2C -> B2B) ===

CONVERSION_MESSAGES = {
    "after_2_reports_bought": {
        "title": "Pensas calcular pensiones seguido?",
        "body": "Si sos contador o asesor financiero, el plan B2B te sale mas barato. Desde $29/mes con multiples clientes.",
        "cta": "Ver planes B2B",
    },
    "after_first_use": {
        "title": "Tu primer calculo esta listo",
        "body": "Guarda tu perfil para volver a usar estos datos sin volver a tipearlos. Modo B2C: 1 perfil gratis. Modo B2B: desde 5 perfiles.",
        "cta": "Crear cuenta",
    },
}



# === Backward Compatibility ===

class TierLimits:
    """Limites por tier (legacy, mantener para no romper imports)."""

    FREE_RPM_PER_DAY = QUOTAS[("b2c", "anonymous")]["calculos_por_dia"]
    PREMIUM_NO_LIMIT = float("inf")
    PRO_PROFILES = QUOTAS[("b2b", "subscriber")]["perfiles"]

    RATE_LIMIT_PER_MINUTE = {
        "free": 5,
        "premium": 30,
        "pro": 60,
    }


class FeatureGate:
    """Legacy feature gate (mantener API para no romper imports)."""

    FEATURES = {
        "calcular_rpm": "free",
        "comparar_regimenes": "premium",
        "calcular_rais": "premium",
        "proyeccion_5_10_15_20": "premium",
        "comparar_3_escenarios": "premium",
        "multiples_perfiles": "pro",
        "exportar_excel": "pro",
    }

    @classmethod
    def can_access(cls, feature: str, user_tier: str) -> bool:
        required_tier = cls.FEATURES.get(feature)
        if required_tier is None:
            return True  # Feature desconocida: gratis
        tier_hierarchy = {"free": 0, "premium": 1, "pro": 2}
        return tier_hierarchy.get(user_tier, 0) >= tier_hierarchy.get(required_tier, 0)

    @classmethod
    def required_tier(cls, feature: str) -> str | None:
        return cls.FEATURES.get(feature)

    @classmethod
    def get_paywall_message(cls, feature: str, current_tier: str) -> dict:
        return {
            "error": "feature_requires_upgrade",
            "feature": feature,
            "current_tier": current_tier,
            "required_tier": cls.required_tier(feature),
        }


def detect_tier_from_request(
    has_premium_cookie: bool = False,
    has_pro_cookie: bool = False,
) -> str:
    """Legacy tier detection (mantener API)."""
    if has_pro_cookie:
        return "pro"
    if has_premium_cookie:
        return "premium"
    return "free"
