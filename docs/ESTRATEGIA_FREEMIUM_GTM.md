# Estrategia Freemium + GTM - pension-calculator

**Producto:** pension-calculator.co (a deployar)
**Owner:** Andres Giraldo (andresgiraldo.com / LinkedIn @andgm)
**Fecha:** 15 oct 2026
**Mercado objetivo primario:** Personas naturales colombianas (B2C) entre 30-65 anos

---

## 🎯 Modelo Freemium

### Principio: "Haz el calculo basico gratis, cobrale al que quiere proyecciones + comparacion"

| Feature | Free | Premium ($5 one-time) | Pro ($15/mes) |
|---------|------|------------------------|----------------|
| Calculo pension RPM basico | ✅ | ✅ | ✅ |
| Ver IBL, tasa, mesada | ✅ | ✅ | ✅ |
| Ver tope/piso legal aplicado | ✅ | ✅ | ✅ |
| PDF reporte basico (1 pagina) | ✅ | ✅ | ✅ |
| **Comparacion RPM vs RAIS** | ❌ | ✅ | ✅ |
| **Proyecciones 5-10-15-20 anos** | ❌ | ✅ | ✅ |
| **3 escenarios macro (Cons/Base/Agr)** | ❌ | ✅ | ✅ |
| **Tabla mortalidad detallada** | ❌ | ✅ | ✅ |
| **Reporte PDF completo (15+ pag)** | ❌ | ✅ | ✅ |
| **Multiples perfiles (familia)** | ❌ | ❌ | ✅ (5 perfiles) |
| **Alertas cambios normativos** | ❌ | ❌ | ✅ |
| **Exportar datos Excel** | ❌ | ❌ | ✅ |
| **Soporte email** | ❌ | ❌ | ✅ (48h) |

### Pricing rationale

- **Free**: Captura trafico SEO + leads email
- **Premium $5 one-time**: Ticket bajo para evitar friccion de suscripcion
- **Pro $15/mes**: Para contadores independientes o planificadores financieros personales

---

## 🛡️ Compliance legal (lo que SI podemos decir)

Lo que SÍ podemos decir:
- "Esta es tu pension estimada en RPM" (calculo puro)
- "Esta seria tu pension estimada en RAIS bajo 3 escenarios" (orientacion)
- "La diferencia entre RPM y RAIS es X" (comparacion factual)
- "Segun Ley 797/2003 Art. X" (cita legal)

Lo que NO podemos decir (asesoria = regulada):
- "Deberias cambiarte a RAIS" (recomendacion personalizada)
- "La AFP X es la mejor para vos" (asesoria especifica)
- "Inverti en fondo Y" (asesoria inversion)
- "Te conviene jubilarte a los 62" (recomendacion personalizada)

**Como lo resolvemos en la UI:**
- Titulos siempre terminan en "...estimada" o "...proyectada"
- Botones dicen "Comparar regimenes" NO "Recomendamos X regimen"
- Footer en cada pagina: "Esto es orientacion educativa, no asesoria financiera personalizada"

---

## 🎨 Landing page - estructura

### Hero (above the fold)
- Titulo: "Calcula tu pension en Colombia en 60 segundos"
- Subtitulo: "Datos oficiales del Banrep y SuperFinanciera. Ley 797/2003 + Decreto 2392/2018"
- CTA: "Calcular gratis" + "Ver reporte premium ($5)"

### Seccion "Como funciona" (3 pasos)
1. "Ingresa tus datos basicos" (fecha nac, sexo, semanas)
2. "Sube tu historia laboral" (opcional, mejora precision)
3. "Recibe tu proyeccion" (gratis para RPM, premium para comparar)

### Seccion "Por que nosotros"
- ✅ Comparacion neutral RPM vs RAIS (las AFPs no te daran esto)
- ✅ Datos oficiales verificados
- ✅ Hecho por Andres Giraldo, MSc Data Analytics UNAL + 7 anos backend
- ✅ Disclaimer legal explicito
- ✅ Codigo abierto (transparencia)

### Seccion "Calculadoras"
- Card 1: Calculadora RPM (gratis)
- Card 2: Comparador RPM vs RAIS ($5)
- Card 3: Proyecciones multi-escenario ($15/mes)

### Seccion "Para contadores"
- Link a /business
- "Cobrale al cliente lo que el contador no sabe explicar"

### Footer con tu perfil
- Foto + nombre + titulo
- Links a GitHub (AndresGM7), LinkedIn (andgm)
- "Senior AI/Backend Engineer | MSc Data Analytics UNAL"

---

## 📣 GTM - Go to Market

### Mes 1-2: Lanzamiento silencioso
- Publicar landing + producto funcional
- Post en LinkedIn con demo
- 1 post en Reddit r/colombia
- Outreach manual a 5 contadores (sin pedir nada, solo feedback)

### Mes 3-4: Trafico organico SEO
- Crear 10 articulos SEO:
  - "Como calcular tu pension en Colombia" (keyword principal)
  - "Diferencia entre Colpensiones y AFP"
  - "Cuanto necesitas cotizar para jubilarte"
  - "Cuanto cobra cada AFP"
  - "Ley 797 de 2003 explicada"
  - etc.
- Indexar en Google Search Console

### Mes 4-6: Validacion pricing
- A/B test del pricing ($3 / $5 / $10)
- Comparar conversion rate
- Iterar segun datos

### Mes 6-12: Escalar
- Si pricing funciona: invertir en ads ($50-100/mes Google Ads)
- Si B2C no funciona: pivotar a B2B contadores

---

## 🎯 Metricas de exito (primer ano)

### Trimestre 1
- 500 visitantes unicos / mes (SEO + posts)
- 50 calculos RPM gratis / mes
- 5 reportes premium vendidos / mes
- Ingresos: $25/mes

### Trimestre 2
- 1,500 visitantes unicos / mes
- 150 calculos / mes
- 15 reportes premium / mes
- 3 suscriptores Pro
- Ingresos: $100/mes

### Trimestre 3-4
- 5,000 visitantes unicos / mes
- 500 calculos / mes
- 50 reportes premium / mes
- 20 suscriptores Pro
- Ingresos: $400/mes

### Ano 1 completo
- 10,000 visitantes/mes
- 1,000 calculos/mes
- 100 reportes premium/mes
- 50 suscriptores Pro
- Ingresos: $1,000-$1,500/mes

---

## 🚫 Lo que NO hacemos (anti-tesis)

1. **NO competimos con Colpensiones/AFPs en su terreno**: ellos calculan su propia pension, nosotros comparamos neutral
2. **NO somos una fintech**: no manejamos dinero de usuarios
3. **NO damos asesoria personalizada**: somos orientacion educativa
4. **NO usamos dark patterns**: pricing claro, cancelacion facil
5. **NO nos asociamos con AFPs**: somos independientes

---

## ✅ Por que esto funciona (tesis)

1. **Gap de mercado real**: NO existe comparador neutral en Colombia
2. **Datos oficiales verificados**: credibilidad que las AFPs no tienen (transparencia)
3. **Trafico SEO capturable**: keywords como "calcular pension colombia" tienen volumen
4. **Pricing bajo**: $5 es ticket de impulso, no suscripcion
5. **Background tecnico del founder**: Senior AI Engineer + MSc Data Analytics + Economista + Financial Engineer = credibilidad unica

---

## 🎬 Proximos pasos concretos

### Hoy (este turno)
- Definir matriz features free/premium ✅
- Mejorar landing page
- Implementar gates API
- Crear /pricing

### Antes del deploy
- Validar flyctl auth (vos lo haces)
- Setup Stripe
- Deploy a Fly.io

### Post-deploy
- Outreach LinkedIn (post fundador)
- Posts SEO (semana 1-2)
- Primeros usuarios beta

---
