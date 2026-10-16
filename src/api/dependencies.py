"""Dependencias de FastAPI para detectar tier del usuario y aplicar gates.

Uso:
    @router.post("/premium-feature")
    async def endpoint(user_tier: UserTierDep = Depends(require_tier("premium"))):
        ...
"""
from fastapi import Cookie, Depends, HTTPException, status

from src.core.billing.feature_gates import (
    FeatureGate,
    detect_tier_from_request,
)


def get_user_tier(
    premium_cookie: str | None = Cookie(default=None, alias="pc_premium"),
    pro_cookie: str | None = Cookie(default=None, alias="pc_pro"),
) -> str:
    """Dependency para detectar el tier del usuario desde cookies.

    En produccion se conectaria con Stripe. Para MVP usamos cookies.
    """
    return detect_tier_from_request(
        has_premium_cookie=premium_cookie is not None,
        has_pro_cookie=pro_cookie is not None,
    )


def require_feature(feature_name: str):
    """Factory para dependency que requiere una feature especifica.

    Args:
        feature_name: nombre de la feature en FeatureGate.FEATURES

    Returns:
        Dependency function que valida el acceso
    """
    def dependency(user_tier: str = Depends(get_user_tier)) -> str:
        if not FeatureGate.can_access(feature_name, user_tier):
            paywall = FeatureGate.get_paywall_message(feature_name, user_tier)
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=paywall,
            )
        return user_tier

    return dependency


def require_tier(min_tier: str):
    """Factory para dependency que requiere tier minimo.

    Args:
        min_tier: "free", "premium", o "pro"
    """
    tier_hierarchy = {"free": 0, "premium": 1, "pro": 2}
    required_level = tier_hierarchy.get(min_tier, 0)

    def dependency(user_tier: str = Depends(get_user_tier)) -> str:
        user_level = tier_hierarchy.get(user_tier, 0)
        if user_level < required_level:
            paywall = FeatureGate.get_paywall_message(
                feature="unknown", current_tier=user_tier
            )
            paywall["required_tier"] = min_tier
            paywall["message"] = f"Esta feature requiere plan {min_tier.title()} o superior."
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=paywall,
            )
        return user_tier

    return dependency


# Type alias for cleaner endpoint signatures
UserTierDep = str
