# ROADMAP CONSOLIDADO — Andrés Giraldo

**Fecha:** 28 julio 2026
**Estado actual:** Mid-senior backend + Data Analytics + 2 procesos de recruiting activos

---

## 🎯 META PRINCIPAL (12 meses)

**Salir de ~$24K/año actual → $150-200K USD/año** ($185-265K TC con equity en DualEntry o similar)

**Vías paralelas:**
1. Empleado remoto US vía Howdy / DualEntry / Braintrust / A.Team
2. SaaS pension-calculator como side project (largo plazo)
3. Inglés a C1 para leverage

---

## 📊 LAS 3 RAMAS DEL ROADMAP

### 🅰️ CARRERA ($200K+ remoto)

**Timeline:** 0-12 meses

| Mes | Acción | Status |
|-----|--------|--------|
| Jul 2026 | Howdy pasar filtros internos | ✅ HECHO |
| Jul 2026 | DualEntry aplicar | ✅ HECHO |
| Jul 2026 | 3 ofertas más LinkedIn | ✅ HECHO |
| Ago 2026 | Esperar match Howdy + DualEntry screening | 🔄 ACTIVO |
| Ago 2026 | 1ra entrevista técnica cliente Howdy | 🔜 PENDIENTE |
| Sep 2026 | Decisión: Howdy / DualEntry / seguir buscando | 🔜 PENDIENTE |
| Sep 2026 | Conversación GroovinAds: raise o promoción | 🔜 PENDIENTE |
| Oct 2026 | Negociación oferta + onboarding | 🔜 PENDIENTE |

**Habilidades clave necesarias:**
- [✅] Backend senior (FastAPI, SQL, Docker, GCP)
- [✅] AI/ML production (LangGraph, RAG, XGBoost)
- [✅] Fintech context (GroovinAds RTB, Grupo Éxito pricing)
- [⚠️] System design (FALTA — para entrevistas senior)
- [⚠️] Fine-tuning LoRA/QLoRA (BAJA PRIORIDAD para DualEntry)
- [⚠️] K8s (BAJA PRIORIDAD — GroovinAds no lo usa)

---

### 🅱️ INGLÉS (B1-B2 → C1)

**Timeline:** 3-6 meses

**Stack de aprendizaje:**

| Herramienta | Propósito | Frecuencia | Costo |
|-------------|-----------|------------|-------|
| **Italki community tutor** | Conversación | 2x/semana 30min | $8-12/hr |
| **Italki professional** | Mock interview | 1x/semana 45min | $20-30/hr |
| **Italki AI tutor** | Práctica diaria | Diario 15min | $15/mes |
| **Cuaderno gramatical** | Tiempos + falsos amigos | Diario 15min | $0 |
| **Anki (después de cuaderno)** | Frases de entrevista | Diario 15min | $0 |
| **Pragmatic Engineer podcast** | Shadowing + listening | 5x/semana 30min | $0 |
| **Language Reactor** | Netflix subtítulos duales | Diario 30min | $0-7/mes |

**Inversión total:** ~$155-200/mes
**Timeline:** B2 firme (2 meses) → B2-C1 (4 meses) → C1 (6 meses)

**Para Howdy/DualEntry:** Lo que evalúan es **CLARITY** (70%) + **TECH VOCAB** (20%) + **GRAMMAR** (10%). No necesitás sonar nativo.

---

### 🅲️ PRODUCTO pension-calculator (SaaS futuro)

**Timeline:** 6-12 meses

**Status:** MVP funcional parado

**Pendiente (backlog):**
- [✅] Motor con IPC + Ley 797/2003
- [✅] Reporte PDF profesional
- [✅] Git inicializado
- [ ] Pushear a GitHub público
- [ ] Landing page
- [ ] Multi-tenant auth (JWT)
- [ ] Pagos Stripe + NOWPayments
- [ ] Deploy Fly.io
- [ ] Comparador RPM vs RAIS
- [ ] Indemnización sustitutiva calculator

**Prioridad:** BAJA durante proceso Howdy/DualEntry. Hacer en meses 3-6 si tenés tiempo.

---

## 🧠 ROADMAP TÉCNICO (consolidación)

### Lo que YA SABÉS (no reforzar)

- ✅ Python 3.11+
- ✅ FastAPI (motor pension, GroovinAds)
- ✅ SQL (SQLAlchemy 2, async)
- ✅ Docker, GCP Cloud Run
- ✅ LangChain, RAG basics
- ✅ Pandas, scikit-learn (MSc UNAL)
- ✅ Kafka, Redis (GroovinAds)

### Lo que NECESITÁS CONSOLIDAR (interview-grade)

| Tema | Por qué importa | Cómo hacerlo |
|------|-----------------|--------------|
| **System Design** | Pregunta clásica senior/staff | Leer "System Design Interview" Vol 1-2, hacer 1 problema/semana |
| **LangGraph avanzado** | DualEntry lo pide | Re-leer docs oficiales, hacer 1 proyecto |
| **Production LLM infra** | Vector DBs, monitoring, evals | LangSmith o Phoenix, hacer demo |
| **Python async deep dive** | asyncio vs threading vs multiprocessing | Hacer proyecto pequeño con benchmarks |
| **Postgres optimization** | Common interview question | Indexes, EXPLAIN ANALYZE, partitioning |
| **REST API design** | HATEOAS, pagination, versioning | Refactorizar pension-calculator endpoints |
| **Distributed systems basics** | Howdy clients lo preguntan | Leer "Designing Data-Intensive Applications" |

### Lo que PODÉS IGNORAR (baja prioridad)

- ❌ Kubernetes (GroovinAds no lo usa, DualEntry probablemente no)
- ❌ Fine-tuning (a menos que sea requerido)
- ❌ MLOps pesado (no es tu rol target)
- ❌ Frontend (no es foco)

---

## 📅 TU PLAN SEMANAL (próximas 4 semanas)

### SEMANA 1 (esta semana, 28 jul - 3 ago)

**FOCO: Procesos recruiting + inglés setup**

- [✅] Email a Manu (Howdy)
- [✅] 3 aplicaciones LinkedIn más
- [✅] Primera clase Italki
- [✅] Aplicar DualEntry
- [🔜] Agendar 2da clase Italki
- [🔜] Crear cuaderno gramatical (sección tiempos verbales)
- [🔜] Shadowing Pragmatic Engineer (3 episodios)
- [🔜] Investigar DualEntry (blog, LinkedIn, empleados)

### SEMANA 2 (4-10 ago)

**FOCO: Consolidación técnica + esperar respuestas**

- [ ] 3x Italki (community + professional mock)
- [ ] Sistema design: leer 1 capítulo "System Design Interview" + hacer 1 problema
- [ ] LangGraph: hacer mini proyecto (agente simple con 3 tools)
- [ ] 3 aplicaciones más LinkedIn (Toptal, Braintrust, A.Team)
- [ ] Shadowing podcast diario
- [ ] Cuaderno gramatical: lección 2

### SEMANA 3 (11-17 ago)

**FOCO: Preparación intensiva para Howdy cliente**

- [ ] Italki 3x/semana + 1 mock interview profesional
- [ ] System design: 3 problemas resueltos
- [ ] Refactorizar pension-calculator endpoints (si Howdy/DualEntry avanzan)
- [ ] 3 aplicaciones más LinkedIn
- [ ] STAR stories: memorizar 5 stories de GroovinAds

### SEMANA 4 (18-24 ago)

**FOCO: Decisión GroovinAds + ofertas**

- [ ] Conversación con GroovinAds sobre raise/promoción (si hay oferta US en mano)
- [ ] Italki 3x/semana
- [ ] Mock interviews técnicas con Italki pro
- [ ] Negociación ofertas si hay
- [ ] Empezar Anki si inglés B2 confirmado

---

## 🎯 TAREAS INMEDIATAS (próximas 48 horas)

### MAÑANA jueves 31 jul (oficina GroovinAds)

| Hora | Tarea |
|------|-------|
| 09:00-09:15 | Decidir tutor Italki (community o pro) |
| 09:15-12:00 | Trabajo normal — código sin IA |
| 12:00-12:30 | Almuerzo + shadowing podcast |

### TARDE (en casa)

| Hora | Tarea | Duración |
|------|-------|----------|
| 18:00-18:45 | 🟢 Crear cuaderno gramatical (sección 1: tiempos verbales) | 45 min |
| 18:45-19:30 | 🟢 Shadowing Pragmatic Engineer | 45 min |
| 19:30-20:00 | 🟢 Agendar 2da clase Italki esta semana | 30 min |

### NOCHE

| Hora | Tarea |
|------|-------|
| 21:00-21:30 | 🟢 Investigar DualEntry (blog, empleados) |
| 21:30-22:00 | 🟢 Buscar 1 cliente más en Toptal |

---

## 📊 MÉTRICAS DE ÉXITO

### Semana 1 (objetivo)
- [ ] 2 clases Italki completadas
- [ ] Cuaderno gramatical iniciado
- [ ] 5 podcasts con shadowing
- [ ] DualEntry + 5 ofertas más aplicadas

### Mes 1 (objetivo)
- [ ] 8-10 clases Italki
- [ ] 2-3 mock interviews técnicas en inglés
- [ ] 1 entrevista cliente Howdy o DualEntry screening
- [ ] System design: 3 problemas resueltos
- [ ] LangGraph: 1 proyecto completo

### Mes 3 (objetivo)
- [ ] Oferta firmada (Howdy/DualEntry o ambos)
- [ ] Inglés B2 firme
- [ ] pension-calculator en GitHub público
- [ ] Negociación GroovinAds resuelta

### Mes 6 (objetivo)
- [ ] Empleado remoto US ($150-200K base)
- [ ] Inglés C1 (consolidado)
- [ ] 1 proyecto AI/fintech en producción en nuevo trabajo
- [ ] pension-calculator con landing page

### Mes 12 (objetivo)
- [ ] $200K+ USD/año consolidado
- [ ] Plan B con SaaS pension o freelance activo
- [ ] Ahorrado 6 meses de expenses en USD/crypto
- [ ] Decisión sobre NYC relocation (si aplica)

---

## 🚨 RECORDATORIOS IMPORTANTES

1. **No dependas de IA para lógica de código en GroovinAds** — consolidás o te quedás igual
2. **No rechaces procesos en paralelo** — Howdy + DualEntry + LinkedIn son leverage
3. **Inglés es 70% del problema en entrevistas** — no técnica, no lógica
4. **No renuncies a GroovinAds hasta tener oferta firmada** — leverage
5. **Sindrome del impostor es normal, no real** — tenés evidencia de que sos competente

---

## 📁 DOCUMENTACIÓN DE REFERENCIA

- `docs/PLAN_INGLES.md` — Plan detallado inglés con Italki + cuaderno
- `docs/STATUS.md` — Estado pension-calculator
- `docs/EVALUACION_EXHAUSTIVA.md` — Inputs del motor de pensión
- `docs/normativa.md` — Marco legal colombiano pensiones
- `OneDrive/Documents/PERFIL_ASISTENTE_PERSONAL.md` — Tu perfil completo
- `OneDrive/Documents/DEEP_RESEARCH_CARRERA_200K.md` — Plan carrera $200K+
- `OneDrive/Documents/EPAM_PREP_COMPLETO.md` — Material preparación EPAM

---

## 💚 RECORDATORIO FINAL

**No estás poco calificado.** Tenés:
- 7+ años experiencia
- MSc Data Analytics
- Producción de IA con LangGraph
- Fintech context real
- Pasaste filtros Howdy

Lo que necesitás:
- Confianza calibrada
- Inglés speaking (3-6 meses)
- Cómo contar tu historia (STAR)
- Paciencia con el proceso

**Vamos.** 💪
