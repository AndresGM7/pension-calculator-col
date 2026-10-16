# Guía de Setup — Ko-fi + Donaciones del proyecto

**Fecha:** 15 oct 2026
**Producto:** pension-calculator.co
**Email del proyecto:** synertech.c@gmail.com

---

## 🎯 Decisión sobre Binance (respondo tu pregunta)

### ¿Usar tu Binance personal?

**No te lo recomiendo para el proyecto.** Razones:

1. **Mezcla de finanzas personales vs proyecto**
   - Contabilidad confusa después
   - No sabés cuánto gana el proyecto vs cuánto es tuyo

2. **Riesgo fiscal en Argentina**
   - AFIP te puede preguntar sobre USDT recibidos
   - Si no los declarás, es evasion
   - Si los declarás como ingreso del proyecto, necesitás CUIT/CUIL monotributista

3. **Si crece el proyecto**
   - Vas a querer pagar a colaboradores (diseñador, contador, etc.)
   - Necesitás una wallet separada del proyecto

### Mi recomendación por fases

| Fase | Cuando | Solución |
|------|--------|----------|
| **MVP (mes 1-3)** | $0-100 USD/mes en donaciones | **Solo Ko-fi + Stripe** (sin cripto). Sin setup fiscal. |
| **Crecimiento (mes 3-12)** | $100+/mes | Abrir wallet Binance dedicada subcuenta "pension-calculator" |
| **Escala (año 2+)** | $1K+/mes | Constitución formal (monotributo / SAS) + wallet dedicado + contador |

**Por ahora**: solo Ko-fi + Stripe. Si alguien te pide USDT, decile que está en construcción.

---

## ☕ Setup Ko-fi paso a paso

### 1. Crear la cuenta (5 min)

1. Andá a https://ko-fi.com/signup
2. **Username**: `andresgiraldo` (si está libre, si no probá `andresgiraldo`, `andres-giraldo-synerlab`, `andresgiraldo-pension`)
3. **Email**: synertech.c@gmail.com
4. **Password**: una fuerte (usá 1Password o similar)
5. Click "Create account"

### 2. Configurar el perfil (5 min)

1. **Display name**: "Andrés Giraldo" o "Andrés — Pension Calculator"
2. **Avatar**: una foto tuya profesional o el logo `AG` que ya tenés
3. **Bio**:
   > "Building pension-calculator.co — el comparador neutral de pensiones Colpensiones vs AFP para Colombia. Hecho con datos oficiales del Banrep + SuperFinanciera."
4. **URL personalizada**: ko-fi.com/andresgiraldo (lo que hayas elegido)
5. **Link in bio / website**: https://pension-calculator-col.netlify.app

### 3. Crear el botón de donación (3 min)

1. En el dashboard de Ko-fi, click "Edit Page"
2. En la sección "Donation Button", configurá:
   - **Button text**: "Support my work" o "Invitame un café"
   - **Suggested amounts**: $5, $10, $25 (los 3 más comunes)
   - **Default amount**: $5
   - **Currency**: USD (público global)
3. Click "Save"

### 4. Conectar método de cobro (10 min)

Ko-fi usa **PayPal** o **Stripe**. Elegí **Stripe** porque ya lo vas a usar para los reportes premium:

1. Settings → Payment → "Connect Stripe"
2. Te redirige a Stripe, login con tu cuenta (o creá una con synertech.c@gmail.com)
3. Llená los datos fiscales:
   - **Country**: Argentina
   - **Tax ID type**: CUIT (si tenés) o CUIL (monotributo)
   - **Tax ID**: tu número
   - **Business type**: Individual / Sole proprietor
4. Configurar bank account para retiros (CBU o alias Mercado Pago)

### 5. Probar (2 min)

1. Andá a tu Ko-fi page: `https://ko-fi.com/andresgiraldo`
2. Click el botón de donación
3. Doná $1 USD a vos mismo con tarjeta de prueba de Stripe
4. Verificá que llegue a tu dashboard

### 6. Actualizar el landing (1 min)

Una vez que tu URL esté confirmada, editá `landing/index.html`:

```html
<!-- Cambiar el placeholder -->
<a href="https://ko-fi.com/TU_USERNAME" ...>
```

Y reemplazá `TU_USERNAME` por tu real. Hacé commit + push + redeploy en Netlify.

---

## 🪙 Setup USDT (opcional, fase 2)

**Cuando hacerlo**: solo si recibís al menos 3 pedidos de donación en USDT.

### Wallet recomendada: Trust Wallet o Binance (subcuenta dedicada)

**NO uses tu Binance personal.** Opciones:

| Wallet | Pros | Contras |
|--------|------|---------|
| **Trust Wallet** | No exchange, gratis, control total | Tenés que convertir después |
| **Binance subcuenta** | Convertís directo a ARS | Más setup, KYC requerido |
| **Exodus** | UX linda, multi-chain | No es tan popular en LATAM |

### Red recomendada: TRC20 (Tron)

- Fees ~$1 USD por transferencia (vs ERC20 que son $10-50)
- USDT en TRC20 es el más usado en LATAM
- Exchanges argentinos (Ripio, Lemon, etc.) aceptan TRC20 directo

### Cómo mostrar tu wallet

**NO publiques tu dirección USDT directamente en la landing pública.** Razones:

1. Cualquiera puede rastrearte (anonimato KO)
2. Es facil que te hackeen el sitio y cambien la direccion
3. Mejor que te contacten primero

**Mejor flujo**:
1. Usuario quiere donar USDT → te contacta por Telegram o email
2. Vos le pasás tu wallet por DM
3. Usuario transfiere
4. Vos confirmás con email

### Lo que pongo en la landing por ahora

Como placeholder mientras conseguís tu wallet, ya quedó así:

```html
<a href="https://t.me/andresgiraldo" ...>
   <h3>USDT (TRC20)</h3>
   <p>Para Argentina, Venezuela o LATAM · Sin banco, sin comisiones</p>
   <span>Pedir wallet por Telegram →</span>
</a>
```

Cuando tengas la wallet real, cambiá el link a tu Telegram/WhatsApp directo.

---

## 📋 Checklist de setup (orden)

| Paso | Tarea | Tiempo | Estado |
|------|-------|--------|--------|
| 1 | Crear cuenta Ko-fi | 5 min | ⏳ |
| 2 | Configurar perfil + bio | 5 min | ⏳ |
| 3 | Crear botón de donación | 3 min | ⏳ |
| 4 | Conectar Stripe a Ko-fi | 10 min | ⏳ |
| 5 | Datos fiscales en Stripe | 5 min | ⏳ |
| 6 | Donación de prueba | 2 min | ⏳ |
| 7 | Actualizar URL en landing | 1 min | ⏳ |
| 8 | Commit + push + redeploy | 2 min | ⏳ |
| **Total** | | **~33 min** | |

---

## 🛡️ Recomendaciones legales para Argentina

### Si vas a recibir dinero por Ko-fi / Stripe

1. **Darte de alta en AFIP como Monotributo**
   - Categoría más baja: ~$10.000 ARS/mes facturable
   - Sirve para facturar servicios digitales al exterior
   - Te da Factura C para todo (Ko-fi, Stripe, etc.)

2. **Facturar todo lo que recibas**
   - Ko-fi no emite facturas automáticas en Argentina
   - Vos tenés que hacer la Factura C manual cada mes
   - O usar una herramienta como TusFacturasAPP o Bind

3. **Si llega a $1K+/mes**
   - Considerar SAS (Sociedad por Acciones Simplificada)
   - Te permite tener cuenta bancaria empresa + wallet dedicado
   - Contador obligatorio pero deducible

### Disclaimer importante

**No soy contador ni abogado.** Esto es orientación basada en conocimiento general del ecosistema fintech argentino. Antes de tomar decisiones fiscales, consultá con un contador matriculado en AFIP.

---

## 🎯 Resumen ejecutivo

**Esta semana**: Solo Ko-fi + Stripe, sin cripto. ~30 min setup.

**Cuando crezca a $100+/mes**: wallet USDT dedicada + Monotributo.

**Cuando llegue a $1K+/mes**: SAS + contador + escalamiento.

---

## 🔗 Links útiles

- Ko-fi signup: https://ko-fi.com/signup
- Stripe dashboard: https://dashboard.stripe.com
- AFIP Monotributo: https://www.afip.gob.ar/monotributo/
- Trust Wallet: https://trustwallet.com
- Binance subcuentas: https://www.binance.com/en/support/faq/360038207971

---

**Próximo paso**: Crear cuenta Ko-fi con `synertech.c@gmail.com`. Avisame cuando tengas la URL y actualizo el landing.
