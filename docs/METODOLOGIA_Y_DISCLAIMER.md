# Metodologia y Disclaimer Legal - pension-calculator

**Version:** 1.0
**Fecha:** 15 de octubre de 2026
**Autor:** Andres Giraldo

---

## 🎯 Objetivo del documento

Este documento describe la metodologia actuarial/financiera usada por
`pension-calculator` y los disclaimers legales que protegen al producto
y al usuario de expectativas incorrectas.

Esta herramienta es **un servicio de estimacion orientativa**, NO reemplaza
el calculo oficial de Colpensiones ni de las AFPs.

---

## 📐 Metodologia del calculo RPM (Regimen de Prima Media - Colpensiones)

### 1. Ingreso Base de Liquidacion (IBL)

**Definicion legal:** Promedio de los salarios sobre los que cotizo la persona
durante los ultimos 10 anos (o toda la vida laboral si es menor).

**Nuestra implementacion:**

1. Tomamos todos los periodos cotizados del usuario (con fechas de inicio/fin y monto)
2. Si el periodo de cotizacion cae dentro de los ultimos 10 anos desde la fecha de
   jubilacion, lo incluimos en la ventana del IBL
3. Para cada periodo, **indexamos el IBC al valor presente** usando el IPC oficial
   del Banrep:
   ```
   IBC_indexado = IBC_original * (IPC_referencia / IPC_periodo)
   ```
4. El IBL es el promedio ponderado de los IBCs indexados

**Fuentes de datos:**
- IPC mensual oficial: Banco de la Republica (Banrep)
  https://www.banrep.gov.co/es/estadisticas/indice-precios-consumidor-ipc
- IPC historico 1954-2026 en: `data/IPC_Índice de Precios al Consumidor.csv`

### 2. Tasa de reemplazo (Ley 797 de 2003)

La tasa de reemplazo determina que porcentaje del IBL recibira como pension.

**Regla oficial (Ley 797 de 2003, art 10):**

| Semanas cotizadas | Tasa base |
|-------------------|-----------|
| 1,300 (minimo)     | 40.0%    |
| 1,300 - 1,800      | 40% + (semanas adicionales / 100) * 2% |
| 1,800+             | Tope maximo 80% |

**Nuestra implementacion:**

```python
def calcular_tasa_reemplazo(semanas: int) -> float:
    if semanas < 1300:
        return 0.0
    if semanas <= 1800:
        return 0.40 + (semanas - 1300) / 100 * 0.02
    return 0.80
```

### 3. Mesada pensional

```
mesada = IBL * tasa_reemplazo
```

### 4. Requisitos de edad y semanas

| Genero | Edad jubilacion | Semanas minimas |
|--------|----------------|-----------------|
| Hombre | 62 anos        | 1,300           |
| Mujer  | 57 anos        | 1,300           |

**Nuestra implementacion:**
- Si no cumple semanas -> NO TIENE DERECHO
- Si cumple semanas pero no edad -> puede proyectar con la fecha de jubilacion
- Tope del IBL: 25 SMLMV (Ley 797 de 2003 art 18)

---

## 📐 Metodologia del calculo RAIS (Regimen de Ahorro Individual)

### 1. Saldo acumulado

Para cada mes entre la fecha actual y la fecha de jubilacion:

```
saldo(t+1) = saldo(t) * (1 + rentabilidad_mensual) - comision_afp + aporte_mensual
```

Donde:
- `aporte_mensual = IBC * (porcentaje_cotizacion + porcentaje_adicional)`
- `rentabilidad_mensual = (1 + rentabilidad_anual)^(1/12) - 1`
- `comision_afp = saldo * comision_anual_pct / 12`

**Fuentes:**
- Rentabilidades nominales por AFP: Carta Circular No.39 del 08 de julio del 2026
  Superintendencia Financiera de Colombia.
  Link directo a la tabla oficial: https://www.colfondos.com.co/dxp/personas/pensiones-obligatorias/conoce-mas/cifras?tab=0
  (Colfondos publica la tabla oficial con rentabilidades de las 4 AFPs).
  Tambien accesible via menu: https://www.colfondos.com.co/ → "Personas" → "Pensiones Obligatorias" → "Conoce mas" → "Cifras"
- Comisiones por AFP: SuperFinanciera (valor publicado 2026)
  https://www.superfinanciera.gov.co/

NOTA: Algunos sitios oficiales (Colpensiones, SuperFinanciera, Colfondos) tienen
bot detection desde fuera de Colombia. Si no podes abrirlos, los datos estan
replicados en nuestro `data/rais_rentabilidades.json` (Carta Circular 39/2026
ya integrada).

### 2. Mesada vitalicia vs retiro programado

**Vitalicia:** se compra un seguro de renta vitalicia con el saldo acumulado.
La mesada depende del saldo y de la expectativa de vida al jubilarse.

**Retiro programado:** la AFP sigue administrando el saldo y paga mesada
mensual hasta que se agote el saldo.

**Nuestra implementacion:**
- Mesada vitalicia = saldo / meses_esperanza_vida (estimacion simple)
- Mesada retiro programado = saldo / meses_esperanza_vida (conservador)
- Esperanza de vida usada: tabla DANE mortalidad Colombia

### 3. Tabla de mortalidad

Se usa la tabla de mortalidad DANE 2018-2023:
- Hombres 62 anos: ~18 anos adicionales (~216 meses)
- Mujeres 57 anos: ~26 anos adicionales (~312 meses)

**Disclaimers:**
- Las tablas de mortalidad cambian con el tiempo
- No usamos tabla de mortalidad propia, usamos dato publico

---

## 📐 Metodologia de proyecciones a multiples horizontes

Para cada horizonte (5, 10, 15, 20 anos):

1. Proyectar IBC futuro con tasa nominal anual = inflacion + crecimiento real
2. Proyectar semanas cotizadas: ~50 semanas/anio continuando cotizacion historica
3. Calcular pension RPM con IBCs proyectados (ventana de ultimos 10 anos)
4. Calcular pension RAIS con aportes proyectados + capitalizacion

**3 escenarios macro:**
- **Conservador:** inflacion alta (5-8%), crecimiento real bajo (0.5%)
- **Base:** inflacion moderada (3-5%), crecimiento real estable (1.5%)
- **Agresivo:** inflacion controlada (2.5-3%), crecimiento real alto (2.5%)

**Fuentes proyecciones:**
- Inflacion esperada: Banrep (encuesta mensual de expectativas)
  https://suameca.banrep.gov.co/estadisticas-economicas/encuestas
- Crecimiento real: estimacion basada en variacion historica SMLMV 2000-2025

---

## 📐 Comparacion de regímenes (RPM vs RAIS)

Mostramos al usuario:
- Pension esperada en RPM (con mesada y tasa reemplazo)
- Pension esperada en RAIS (saldo, mesada vitalicia, retiro programado)
- Diferencia absoluta y porcentual
- Recomendacion: NO es asesoria financiera, es orientacion

**Criterio de recomendacion:**
- Si RPM > RAIS por >15%: sugerir quedarse en RPM
- Si RAIS > RPM por >15%: sugerir evaluar traslado a RAIS
- Diferencia <15%: INDECISO (depende de circunstancias individuales)

---

## ⚖️ DISCLAIMER LEGAL

### Importante: lea antes de usar este producto

**1. NATURALEZA DEL SERVICIO**

`pension-calculator` es una herramienta de **estimacion orientativa** que
proyecta la posible pension de una persona bajo diferentes escenarios.

NO es:
- Asesoria financiera personalizada
- Asesoria juridica
- Un servicio de actuaria certificado
- Una garantia de que la pension sera X monto

NO reemplaza:
- Consulta con Colpensiones
- Consulta con su AFP (Porvenir, Proteccion, Skandia, Colfondos, Old Mutual)
- Asesoria de un asesor financiero certificado

### 2. LIMITACIONES DE LOS CALCULOS

- Los calculos usan **promedios y tasas asumidas**. Los resultados reales pueden
  variar significativamente.
- Las proyecciones a futuro **asumen escenarios que pueden no cumplirse**.
- Las rentabilidades historicas de las AFPs **NO son indicativas de futuros
  resultados** (advertencia textual de la Superintendencia Financiera).
- La metodologia de calculo del IBL puede cambiar con reformas legales.
- Los datos macroeconomicos (inflacion, IPC, SMLMV) son estimados con base en
  datos oficiales del Banrep, pero pueden no reflejar cambios futuros.

### 3. FUENTES DE DATOS

Todas las fuentes son oficiales:
- IPC: Banco de la Republica (Banrep) - DANE
- SMLMV historico: Banco de la Republica (Banrep) - Mintrabajo
- Expectativas de inflacion: Banrep - Encuesta mensual
- Rentabilidades AFP: Superintendencia Financiera - Carta Circular 39/2026
- Topes legales: Ley 797 de 2003 - Decreto 1833 de 2016

### 4. MARCO LEGAL COLOMBIANO

El calculo se basa en:
- Ley 100 de 1993 (Sistema General de Pensiones)
- Ley 797 de 2003 (Reforma Pensional)
- Decreto 1833 de 2016 (Reglamentario)
- Decreto 2392 de 2018 (metodologia rentabilidad AFP)
- Decreto 59 de 2018 (rentabilidad minima obligatoria AFP)
- Carta Circular No.39 del 08 de julio del 2026 (SuperFinanciera)

**Cualquier reforma posterior a septiembre de 2026 NO esta incorporada automaticamente.**

### 5. PROTECCION DEL USUARIO

El producto implementa las siguientes protecciones:

1. **Disclaimer visible** en landing page y reportes generados
2. **Texto legal** en cada PDF exportado
3. **Limitacion de responsabilidad** en terminos y condiciones
4. **Aviso explicito** de que el calculo es estimativo

### 6. PROTECCION DEL DESARROLLADOR

Para el desarrollador:
- Mantener actualizado el motor con cambios legales
- Mostrar fecha de ultima actualizacion de los datos
- Indicar version del motor en cada reporte
- Documentar las asunciones usadas en cada calculo
- NO dar recomendaciones financieras personalizadas
- NO recibir comision por recomendaciones de traslado de regimen

---

## 📋 VERSIONAMIENTO DEL MOTOR

| Version | Fecha       | Cambios principales |
|---------|-------------|---------------------|
| v1.0    | 2026-10-15  | Lanzamiento inicial con RPM, RAIS, comparacion y proyecciones |
| v1.1    | Pendiente   | Datos reales AFP (cuando se obtengan via scraping/API) |
| v2.0    | Pendiente   | Soporte para regimen de transicion (Ley 2381 de 2024) si aplica |

---

## 🔗 Referencias para auditoria

Cualquier auditor o abogado puede:

1. **Verificar metodologia:** este documento + codigo fuente en github.com/AndresGM7/pension-calculator
2. **Verificar datos:** todos los JSON en `data/` tienen campo `_fuente` y `_url`
3. **Verificar calculos:** tests automatizados en `tests/` con pytest
4. **Verificar marco legal:** todos los decretos y leyes citados estan en fuentes oficiales

---

## 📧 Contacto y reporte de errores

Si encuentra una inconsistencia en el calculo o datos:
- Email: [configurar]
- GitHub: https://github.com/AndresGM7/pension-calculator/issues

---

*Ultima actualizacion: 15 de octubre de 2026*
*Version del motor: v1.0*
