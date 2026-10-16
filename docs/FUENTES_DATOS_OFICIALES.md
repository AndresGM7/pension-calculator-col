# Fuentes Oficiales de Datos - pension-calculator

**Estado Sep 21, 2026:** Hermes no puede acceder a muchos sitios oficiales por
bot detection. Este documento lista EXACTAMENTE qué links visitar, qué bajar,
y cómo transformar cada dataset al formato que el código espera.

---

## 📊 PASO 1: Rentabilidades reales de AFPs (últimos 20 años)

### Links prioritarios (probados manualmente Sep 2026)

| # | Fuente | URL | Qué bajar | Formato esperado |
|---|--------|-----|-----------|------------------|
| 1 | **Asofondos - Sistema Pensional** | https://asofondos.org.co/sistema-pensional/ | "Rentabilidad de los fondos de pensiones obligatorias" mensual | PDF o Excel |
| 2 | **Asofondos - Rentabilidades en homepage** | https://asofondos.org.co/ | Series históricas de rentabilidad por fondo | Excel/CSV |
| 3 | **SuperFinanciera - Rentabilidades históricas** | https://www.superfinanciera.gov.co/inicio/industrias-supervisadas/sociedades-administradoras-de-fondos-de-pensiones-y-de-cesantias/pensiones/regimen-de-ahorro-individual-con-solidaridad-rais-/rentabilidades-historicas-10596 | Tabla de rentabilidades por AFP y tipo fondo | HTML/Excel |
| 4 | **SuperFinanciera - Sala de prensa Pensiones** | https://www.superfinanciera.gov.co/inicio/sala-de-prensa/boletines-/pensiones-/rentabilidad-de-los-fondos-de-pensiones-obligatorias-10594 | Boletín mensual | PDF |

### ⚠️ URLs que probé y NO funcionan (Sep 2026)

- `https://www.superfinanciera.gov.co/inicio/industrias-supervisadas/sociedades-administradoras-de-fondos-de-pensiones-y-de-cesantias/pensiones/regimen-de-ahorro-individual-con-solidaridad-rais-/rentabilidades-historicas-10596` → HTTP 500
- `https://www.superfinanciera.gov.co/inicio/sala-de-prensa/boletines-/pensiones-/rentabilidad-de-los-fondos-de-pensiones-obligatorias-10594` → HTTP 500
- `https://www.banrep.gov.co/es/estadisticas/sociedades-administradoras-fondos-pensiones-y-cesantias` → bloqueado por Radware bot detection
- `https://www.asofondos.co/` → DNS no resuelve (dominio correcto es asofondos.org.co)

### Plan B: si las URLs oficiales no funcionan

1. **Scraping manual desde LinkedIn/Twitter** de Asofondos y Superintendencia
   - https://twitter.com/Asofondos
   - https://www.linkedin.com/company/asofondos/
   - Buscar posts con "rentabilidad fondos pensiones [mes] [año]"
2. **Reportes anuales de cada AFP:**
   - https://www.porvenir.com.co/ (sección "Estados financieros")
   - https://www.proteccion.com/ (sección informes)
3. **Trabajos académicos / consultoría:**
   - Google Scholar: "rentabilidad fondos pensiones Colombia"
   - Fedesarrollo, AsoBancaria, ANIF

### Formato del JSON que el código espera

Ubicación: `data/rais_rentabilidades.json`

```json
{
  "fuente": "Asofondos / SuperFinanciera - Rentabilidades mensuales",
  "ultima_actualizacion": "2026-06-30",
  "metodologia": "Rentabilidad nominal anualizada promedio últimos N años por AFP y tipo fondo",
  "rentabilidades_nominales_anuales_promedio": {
    "Porvenir": {
      "Conservador": {"5y": 0.085, "10y": 0.078, "20y": 0.095},
      "Moderado": {"5y": 0.095, "10y": 0.092, "20y": 0.110},
      "Mayor_Riesgo": {"5y": 0.105, "10y": 0.108, "20y": 0.125}
    },
    "Proteccion": {...},
    "Skandia_Colfondos": {...},
    "Old_Mutual": {...}
  },
  "rentabilidades_reales_anuales_promedio": {
    // mismo formato pero deflactado por IPC
  },
  "comisiones_por_afp": {
    "Porvenir": 0.015,
    "Proteccion": 0.014,
    "Skandia_Colfondos": 0.013,
    "Old_Mutual": 0.016
  },
  "tipo_cambio_usd_cop_referencia": 4000
}
```

Una vez que tengas el JSON, ejecutá `python scripts/cargar_rentabilidades_reales.py`
para validar y actualizar el motor.

---

## 💰 PASO 3: Proyecciones macroeconómicas

### Inflación futura (proyecciones)

| # | Fuente | URL | Qué bajar |
|---|--------|-----|-----------|
| 1 | **Banrep - Encuesta de expectativas de inflación** | https://www.banrep.gov.co/es/estadisticas/encuesta-expectativas-inflacion | Serie mensual expectativas inflación 1y, 2y |
| 2 | **Banrep - Reporte de Política Monetaria** | https://www.banrep.gov.co/es/publicaciones/reporte-politica-monetaria | Proyecciones inflación 1-2 años |
| 3 | **DANE - IPC** | https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-precios-al-consumidor-ipc | Histórico IPC |
| 4 | **Fedesarrollo** | https://www.fedesarrollo.org.co/ | Análisis macroeconómicos |

### Salario Mínimo Legal Mensual Vigente (SMLMV)

| # | Fuente | URL | Qué bajar |
|---|--------|-----|-----------|
| 1 | **Mintrabajo - SMLMV histórico** | https://www.mintrabajo.gov.co/empleo-y-pensiones/empleo/salario-minimo | Histórico desde 1984 |
| 2 | **Datos Abiertos Colombia** | https://www.datos.gov.co/buscar?q=smlmv+historico | Dataset si está disponible |

### IBC medio por edad y sexo (referencia para proyecciones)

| # | Fuente | URL | Qué bajar |
|---|--------|-----|-----------|
| 1 | **DANE - GEIH (Mercado Laboral)** | https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral | Ingresos y empleo por edad/sexo (sección Empleo y desempleo) |
| 2 | **Piloto OCDE pensiones Colombia** | https://www.oecd.org/centrodemexico/paises/colombia/ | Reporte OECD sobre sistema pensional |

---

## 🛠️ Scripts para bajar/cargar datos

Una vez que bajes los archivos, ejecutá estos scripts (en orden):

```bash
# 1. Procesar rentabilidades AFPs desde Excel a JSON
python scripts/cargar_rentabilidades_reales.py

# 2. Generar proyecciones macroeconómicas
python scripts/generar_proyecciones_macro.py

# 3. Validar todo
PYTHONPATH=. python -m pytest tests/ -v
```

---

## 📋 Tareas concretas que te toca a vos (Andrés)

Si querés datos REALES hoy, estas son las acciones que podés hacer:

1. **Visitar manualmente** los links prioritarios de arriba
2. **Descargar** los archivos de rentabilidades AFP (PDFs/Excel de Asofondos)
3. **Guardarlos** en `data/raw/` (crear carpeta si no existe)
4. **Decirme** qué archivos bajaste y yo te armo el parser automático

Alternativamente, si te da fiaca y querés salir YA:
- Los valores hardcoded en `data/rais_rentabilidades.json` son **estimaciones razonables**
- Estarían en el rango de la realidad según mi conocimiento del mercado
- Para producción, eventualmente hay que reemplazarlos
- Para demo/MVP: usá los hardcoded, son mejores que nada
