# Guia de Setup — Ko-fi + Donaciones del proyecto

**Fecha:** 15 oct 2026
**Producto:** pension-calculator.co
**Email del proyecto:** synertech.c@gmail.com
**Monotributo:** YA activo (bien, ahorras el setup fiscal)

---

## 🎯 Decision sobre Binance (respondo tu pregunta)

### ¿Usar tu Binance personal para recibir USDT?

**Mi recomendacion: SI, con cuidado.** Razones:

1. **Ya lo tenes** - sin setup adicional
2. **Ya estas en Monotributo** - podes declarar los ingresos
3. **Wallet personal sigue siendo OK** para volumen bajo (< $100/mes)
4. **NO mezclar cony finanzas personales grandes** - solo ingresos del proyecto

### Como hacerlo bien con Binance personal

| Que hacer | Que NO hacer |
|-----------|--------------|
| Etiquetar transacciones como "pension-calculator" | Mezclar gastos personales con ingresos del proyecto |
| Anotar fecha + monto en una planilla simple | Confiar en la memoria |
| Declarar en Monotributo si pasa $X/mes | Ignorar los movimientos |
| Usar solo red TRC20 (fees bajos) | Usar ERC20 (fees altos) |

### Cuando migrar a wallet dedicado

- Cuando recibas > 5 donaciones crypto/mes
- Cuando quieras vender NFT o productos digitales desde el proyecto
- Cuando factures > $1K USD/mes en crypto (ahi si SAS obligatoria)

---

## ☕ Setup Ko-fi - Guia completa paso a paso

Ko-fi te ofrece 4 modelos de monetizacion. Para pension-calculator **recomiendo usar la opcion "Receive tips"** porque es lo mas simple y rapido para empezar.

### Las 4 opciones explicadas

| Opcion | Para que sirve | Ideal para vos? |
|--------|----------------|-----------------|
| **Receive tips** | Donaciones unicas, sin compromiso | **SI, empezar aca** |
| **Build monthly membership** | Suscripcion mensual con beneficios exclusivos | NO todavia (cuando tengas 50+ usuarios) |
| **Sell products** | Vender PDFs, cursos, ebooks | Tal vez despues (vender reportes PDF) |
| **Offer commissions or services** | Ofrecer consultoria 1:1 pagada | NO en MVP (rompe la neutralidad del producto) |

### Paso 1: Crear la cuenta (5 min)

1. Anda a https://ko-fi.com/signup
2. Username: `andresgiraldo` (si esta libre)
3. Email: **synertech.c@gmail.com**
4. Password: una fuerte (usa 1Password o similar)
5. Click "Create account"

### Paso 2: Configurar el perfil (5 min)

1. Display name: "Andres Giraldo"
2. Avatar: una foto profesional o el logo AG
3. Bio:
   > "Building pension-calculator.co - el comparador neutral de pensiones Colpensiones vs AFP para Colombia. Hecho con datos oficiales del Banrep + SuperFinanciera."
4. URL personalizada: ko-fi.com/andresgiraldo
5. Link in bio / website: https://pension-calculator-col.netlify.app

### Paso 3: Elegir tipo de earn (RECOMENDADO: Receive tips)

En el dashboard de Ko-fi:

1. Anda a la seccion **"How are you planning to earn?"**
2. **Marca SOLO "Receive tips"** (las otras 3 las podes activar despues)
3. Esto te permite recibir donaciones unicas sin complejidad

### Paso 4: Configurar el boton de donaciones (3 min)

1. En el dashboard, click **"Edit Page"**
2. En la seccion **"Donation Button"**:
   - Button text: **"Support my work"** o **"Invitame un cafe"**
   - Suggested amounts: **$5, $10, $25**
   - Default amount: **$5**
   - Currency: **USD**
3. Click **"Save"**

### Paso 5: Conectar Stripe (10 min)

Ko-fi usa **PayPal** o **Stripe**. **Elegi Stripe** porque:

1. **Ya lo tenes semi-configurado** del proyecto automations_wp (aunque no este implementado, sabes el flujo)
2. **Fees mas bajos** que PayPal en LATAM (2.9% + $0.30 vs 3.5% + $0.49)
3. **Mejor para vender reportes PDF** despues (cuando agreguemos el pago de $5 USD del reporte premium)
4. **Misma cuenta para Ko-fi y para pension-calculator**

Pasos:

1. Settings → **Payment** → "Connect Stripe"
2. Te redirige a Stripe, login con tu cuenta existente o crea una con synertech.c@gmail.com
3. Llena los datos fiscales:
   - **Country**: Argentina
   - **Tax ID type**: **CUIT** (monotributo)
   - **Tax ID**: tu numero
   - **Business type**: Individual / Sole proprietor
4. Configurar **bank account** para retiros (CBU o alias Mercado Pago)

### Paso 6: Probar (2 min)

1. Anda a tu Ko-fi page: `https://ko-fi.com/andresgiraldo`
2. Click el boton de donacion
3. Dona **$1 USD** a vos mismo con tarjeta de prueba de Stripe
4. Verifica que llegue a tu dashboard de Stripe

### Paso 7: Actualizar el landing (1 min)

Una vez que tu URL este confirmada, edita `landing/index.html`:

```html
<!-- Buscar -->
<a href="https://ko-fi.com/andresgiraldo" ...>

<!-- Reemplazar por tu URL real -->
<a href="https://ko-fi.com/TU_USERNAME" ...>
```

Y hace commit + push + redeploy en Netlify.

### Paso 8: Activar las otras opciones de earn (mes 2-3)

Cuando tu producto tenga traccion, podes volver al dashboard y activar:

- **Monthly membership** ($5/mes): "Acceso prioritario + alertas de cambios normativos"
- **Sell products** ($5-15): "Reporte PDF completo de tu pension (mismo que el premium)"
- **Commissions** (NO recomendado por ahora): romperia la neutralidad

---

## 🪙 Setup USDT con tu Binance personal

### Flujo recomendado

1. **Usuario te contacta** por Telegram/email pidiendo donacion USDT
2. **Vos le pasas tu wallet TRC20** por DM (NO publiques en la landing)
3. **Usuario transfiere** USDT a tu Binance
4. **Vos confirmas** por email + registras en planilla
5. **Mensualmente** declaras en Monotributo

### Como obtener tu direccion TRC20 en Binance

1. Login en https://www.binance.com
2. Wallet → Fiat and Spot
3. Buscar USDT → Deposit
4. Red: **TRC20 (Tron)**
5. Copiar la direccion (empieza con T, 34 caracteres)

### Donde publicar tu wallet

**NO publiques tu direccion directamente en la landing publica.** Razones:

1. Privacidad (cualquiera puede rastrearte)
2. Seguridad (si hackean la landing, cambian tu direccion)
3. Conversacion humana (te permite agradecer y conectar)

### Que pongo en la landing por ahora

Como placeholder, ya quedo asi:

```html
<a href="https://t.me/andresgiraldo" ...>
   <h3>USDT (TRC20)</h3>
   <p>Para Argentina, Venezuela o LATAM · Sin banco, sin comisiones</p>
   <span>Pedir wallet por Telegram →</span>
</a>
```

Cuando tengas tu wallet TRC20 lista, podes:

**Opcion A**: Cambiar el link a tu Telegram directo (lo que esta ahora)
**Opcion B**: Publicar tu wallet directamente + nota "Solo TRC20, no otros redes"

### Planilla simple de donaciones crypto

Crea un Excel/Sheets con estas columnas:

| Fecha | Monto USD | Monto USDT | Red | De (email/telegram) | Concepto |
|-------|-----------|------------|-----|---------------------|----------|
| 2026-10-20 | $25 | 25 USDT | TRC20 | juan@gmail.com | Donacion Ko-fi |
| 2026-10-22 | $10 | 10 USDT | TRC20 | @maria_telegram | Donacion voluntaria |

---

## 📋 Checklist de setup (orden recomendado)

| Paso | Tarea | Tiempo | Estado |
|------|-------|--------|--------|
| 1 | Crear cuenta Ko-fi | 5 min | ⏳ |
| 2 | Configurar perfil + bio | 5 min | ⏳ |
| 3 | Marcar "Receive tips" en earn | 1 min | ⏳ |
| 4 | Configurar boton de donacion | 3 min | ⏳ |
| 5 | Conectar Stripe a Ko-fi | 10 min | ⏳ |
| 6 | Datos fiscales en Stripe (CUIT monotributo) | 5 min | ⏳ |
| 7 | Donacion de prueba | 2 min | ⏳ |
| 8 | Actualizar URL en landing | 1 min | ⏳ |
| 9 | Commit + push + redeploy Netlify | 2 min | ⏳ |
| **Total** | | **~35 min** | |

---

## 🛡️ Recomendaciones legales para Argentina

### Si vas a recibir dinero por Ko-fi / Stripe

1. **Monotributo ya activo** (perfecto, no necesitas mas setup)
2. **Facturar todo lo que recibas** como servicio digital
   - Ko-fi no emite facturas automaticas en Argentina
   - Vos tenes que hacer la Factura C manual cada mes
   - O usar una herramienta como TusFacturasAPP o Bind

3. **Si llega a $1K+/mes**
   - Considerar SAS (Sociedad por Acciones Simplificada)
   - Te permite tener cuenta bancaria empresa + wallet dedicado
   - Contador obligatorio pero deducible

### Para USDT recibido

1. **Anotar cada donacion** en planilla con fecha + monto +TX hash
2. **Declarar mensualmente** como ingreso por servicios
3. **Si convertis USDT a ARS** (vender en Binance P2P), ese movimiento tambien es fiscal

### Disclaimer importante

**No soy contador ni abogado.** Esto es orientacion basada en conocimiento general del ecosistema fintech argentino. Antes de tomar decisiones fiscales, consulta con un contador matriculado en AFIP.

---

## 🎯 Resumen ejecutivo

**Esta semana**: Solo Ko-fi (Receive tips) + Stripe, sin cripto. ~35 min setup.

**Cuando alguien te pida USDT** (mes 1-3): pasar wallet TRC20 de tu Binance personal por Telegram/email.

**Cuando crezca a $100+/mes**: evaluar si conviene wallet dedicado o quedarse con Binance personal.

**Cuando llegue a $1K+/mes**: SAS + contador + escalamiento.

---

## 🔗 Links utiles

- Ko-fi signup: https://ko-fi.com/signup
- Stripe dashboard: https://dashboard.stripe.com
- AFIP Monotributo: https://www.afip.gob.ar/monotributo/
- Binance USDT deposit: https://www.binance.com/en/my/wallet/account/main/deposit/crypto/USDT

---

**Proximo paso**: Crear cuenta Ko-fi con synertech.c@gmail.com y marcar "Receive tips". Avisame cuando tengas la URL y actualizo el landing.
