# Checklist de Secretos - pension-calculator

## Estado verificado Sep 21, 2026

### ✅ Lo que YA está bien
- [x] `.env` en `.gitignore`
- [x] `data/` (con historia laboral personal) en `.gitignore`
- [x] `reporte_francisco.html/pdf` en `.gitignore`
- [x] Solo 2 commits en git, ninguno commitea secretos
- [x] Secretos en `.env` son placeholders marcados para rotar (`dev-secret-key-rotate-now`)

### ⚠️ Lo que hay que hacer ANTES de deploy a producción

#### 1. Generar SECRET_KEY real
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### 2. Generar JWT_SECRET real
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### 3. Configurar Stripe (solo cuando vayas a cobrar)
- Crear cuenta en https://dashboard.stripe.com/
- Obtener `STRIPE_API_KEY` (live key, NO test)
- Crear productos: Reporte Básico ($0), Reporte Premium ($5)
- Obtener `STRIPE_PRICE_*` IDs
- Configurar webhook endpoint
- Obtener `STRIPE_WEBHOOK_SECRET`

#### 4. Configurar NOWPayments (para crypto)
- Crear cuenta en https://nowpayments.io/
- Obtener `NOWPAYMENTS_API_KEY`
- Configurar IPN callback URL
- Obtener `NOWPAYMENTS_IPN_SECRET`

#### 5. Configurar secrets en Fly.io (NO en .env)
```bash
fly secrets set SECRET_KEY=<valor_real>
fly secrets set JWT_SECRET=<valor_real>
fly secrets set STRIPE_API_KEY=sk_live_...
fly secrets set STRIPE_WEBHOOK_SECRET=whsec_...
fly secrets set NOWPAYMENTS_API_KEY=...
fly secrets set DATABASE_URL=postgresql://...
```

### 📋 Política de secretos
- NUNCA commitear `.env` al repo
- Rotar secretos cada 90 días
- Usar distintos secretos para dev/staging/prod
- Si un secreto se filtra: rotar inmediatamente + revisar logs
