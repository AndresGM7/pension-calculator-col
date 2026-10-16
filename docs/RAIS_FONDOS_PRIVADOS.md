# Guía para Ampliar el Servicio a Fondos Privados (RAIS)

**Andrés Giraldo** · Sep 2026
**Estado:** Diseño completo, implementación pendiente (post-deploy público)

---

## 🎯 Lo que esta guía responde

Tu motor actual calcula pensión del **Régimen de Prima Media (RPM)** administrado por Colpensiones. Colombia tiene un segundo régimen: el **Régimen de Ahorro Individual con Solidaridad (RAIS)** administrado por fondos privados (Porvenir, Protección, Skandia/Colfondos, Old Mutual). Esta guía te muestra cómo extender el motor para comparar ambos regímenes.

---

## 📚 Marco Legal Rápido (Colombia)

### Ley 100/1993 — Sistema General de Pensiones
Creó los dos regímenes como alternativas. Todo colombiano debe estar afiliado a UNO:

| Régimen | Administrador | Cómo funciona |
|---|---|---|
| **RPM** (Prima Media) | Colpensiones (público) | Pagas cotizaciones, el Estado te paga una mesada calculada con la fórmula legal |
| **RAIS** (Ahorro Individual) | AFPs privadas | Pagas cotizaciones, van a tu cuenta individual, al jubilarte recibes lo acumulado + rentabilidad |

### Cotizaciones (ambos regímenes)

| Concepto | Porcentaje | Quién paga |
|---|---|---|
| Pensión | 10.0% del IBC | Empleador (75%) + Empleado (25%) |
| FSP (Fondo de Solidaridad Pensional) | 1.0% - 2.0% del IBC | Solo Empleado |
| Total obligatorio | ~11.0% - 12.0% del IBC | Mixto |

### AFPs autorizadas (Sep 2026)
- Porvenir
- Protección
- Skandia (ahora Colfondos)
- Old Mutual (antes Caxdair)

Cada AFP cobra comisión: 0.5% a 3.5% sobre el IBC, varía por AFP y tipo de fondo (Conservador/Moderado/Mayor Riesgo).

---

## 🧮 Matemática del RAIS

### Fórmula de capitalización mensual

```
Para cada mes t:
    Aporte_mes(t) = IBC(t) × (porcentaje_cotizacion + porcentaje_adicional)
    Saldo(t+1) = Saldo(t) × (1 + r_mensual) + Aporte_mes(t)
    
Donde:
    r_mensual = (1 + r_anual)^(1/12) - 1
    r_anual = rentabilidad promedio del fondo (real, no nominal)
```

### Cálculo de la mesada al jubilarse

**No es una "tasa de reemplazo" como en RPM.** En RAIS:

```
1. Calcular saldo total al momento de jubilación
2. Aplicar tablas de mortalidad (DANE/Supersalud) para calcular expectativa de vida
3. La mesada = saldo_total / meses_de_expectativa_de_vida
4. La mesada se ajusta anualmente por IPC
```

**Opciones de mesada en RAIS:**
- **Renta vitalicia**: contratas con una aseguradora, te paga hasta que morís
- **Retiro programado**: te pagan de tu propio saldo mes a mes (se acaba si vivís mucho)
- **Retiro parcial + ahorro remanente**: combinás ambos

---

## 🔧 Implementación Propuesta

### Paso 1: Nuevos inputs

```python
# src/core/pension/rais.py

from dataclasses import dataclass
from datetime import date
from typing import Literal


@dataclass(frozen=True)
class RaisInput:
    """Inputs para cálculo de pensión bajo RAIS."""
    
    # Saldo inicial (si la persona ya tiene dinero acumulado)
    saldo_inicial: float = 0.0
    fecha_saldo_inicial: date | None = None
    
    # Aportes
    porcentaje_cotizacion: float = 0.10  # 10% obligatorio
    porcentaje_adicional: float = 0.0    # Aportes voluntarios del trabajador
    
    # Rentabilidad esperada (anual real, ajustar por tipo de fondo)
    rentabilidad_anual: float = 0.05  # 5% real anual como default conservador
    
    # Tipo de fondo (afecta rentabilidad histórica)
    tipo_fondo: Literal["Conservador", "Moderado", "Mayor_Riesgo"] = "Moderado"
    
    # Comisión AFP (varía por administradora)
    comision_afp: float = 0.015  # 1.5% sobre IBC como default
    
    # Para cálculo de mesada: expectativa de vida o retiro programado
    modalidad: Literal["renta_vitalicia", "retiro_programado"] = "retiro_programado"
    edad_jubilacion: int = 62
```

### Paso 2: Proyección mes a mes

```python
# src/core/pension/rais.py (continuación)

def proyectar_saldo_rais(
    periodos: list[PeriodoCotizacion],
    rais_input: RaisInput,
    fecha_inicio: date,
    fecha_jubilacion: date,
) -> float:
    """Proyecta el saldo acumulado al momento de jubilación."""
    
    saldo = rais_input.saldo_inicial
    r_mensual = (1 + rais_input.rentabilidad_anual) ** (1/12) - 1
    
    # Filtrar periodos hasta fecha de jubilación
    periodos_relevantes = [
        p for p in periodos 
        if p.fecha_inicio < fecha_jubilacion
    ]
    
    for periodo in periodos_relevantes:
        meses = max(1, (periodo.fecha_fin - periodo.fecha_inicio).days // 30)
        # Aporte mensual = IBC × (cotización + adicional) × (1 - comisión AFP)
        aporte_bruto = periodo.ibc * (
            rais_input.porcentaje_cotizacion + rais_input.porcentaje_adicional
        )
        aporte_neto = aporte_bruto * (1 - rais_input.comision_afp)
        
        for _ in range(int(meses)):
            saldo = saldo * (1 + r_mensual) + aporte_neto
    
    return saldo


def calcular_mesada_rais(
    saldo_final: float,
    edad_jubilacion: int,
    sexo: Literal["M", "F"],
    modalidad: Literal["renta_vitalicia", "retiro_programado"],
) -> tuple[float, float]:
    """Calcula la mesada mensual esperada bajo RAIS.
    
    Returns:
        (mesada_mensual, meses_duracion_estimada)
    """
    if modalidad == "retiro_programado":
        # Asumimos 20 años de retiro (240 meses) como base conservadora
        # En realidad se calcula con tablas de mortalidad
        meses = 240
        return (saldo_final / meses, meses)
    
    # renta_vitalicia: depende de tasa de interés técnico de la aseguradora
    # Asumimos 3% real anual como default
    meses = 240  # Simplificación
    return (saldo_final / meses, meses)
```

### Paso 3: Comparación de regímenes

```python
# src/core/pension/comparacion.py

@dataclass(frozen=True)
class ComparacionRegimenes:
    rpm_mesada: float
    rpm_ibl: float
    rpm_tasa: float
    
    rais_saldo_acumulado: float
    rais_mesada_vitalicia: float
    rais_mesada_retiro_programado: float
    
    diferencia: float  # rais - rpm
    regimen_recomendado: Literal["RPM", "RAIS"]
    observaciones: list[str]


def comparar_regimenes(
    rpm_result: PensionResult,
    rais_input: RaisInput,
    periodos: list[PeriodoCotizacion],
    sexo: Literal["M", "F"],
    edad_jubilacion: int,
) -> ComparacionRegimenes:
    """Compara pensión esperada en RPM vs RAIS."""
    
    fecha_jubilacion = date.today().replace(year=date.today().year + (edad_jubilacion - 62))
    saldo_rais = proyectar_saldo_rais(periodos, rais_input, date.today(), fecha_jubilacion)
    mesada_vitalicia, _ = calcular_mesada_rais(saldo_rais, edad_jubilacion, sexo, "renta_vitalicia")
    mesada_retiro, _ = calcular_mesada_rais(saldo_rais, edad_jubilacion, sexo, "retiro_programado")
    
    mejor_rais = max(mesada_vitalicia, mesada_retiro)
    diferencia = mejor_rais - rpm_result.mesada_pensional
    
    recomendado = "RAIS" if diferencia > 0 else "RPM"
    
    obs = []
    if abs(diferencia) < rpm_result.mesada_pensional * 0.1:
        obs.append("Los regímenes dan resultados similares. Otros factores pueden ser decisivos (seguridad, herencia, etc.)")
    elif diferencia > 0:
        obs.append(f"RAIS da ${diferencia:,.0f}/mes más que RPM en este escenario")
    else:
        obs.append(f"RPM da ${abs(diferencia):,.0f}/mes más que RAIS en este escenario")
    
    return ComparacionRegimenes(...)
```

### Paso 4: Endpoint nuevo

```python
# src/api/routes/pension.py (agregar)

@router.post("/comparar-regimenes")
async def comparar_regimenes(request: ComparacionRequest):
    """Compara pensión esperada en RPM (Colpensiones) vs RAIS (AFPs privadas)."""
    rpm_input = PensionInput(
        fecha_nacimiento=request.fecha_nacimiento,
        sexo=request.sexo,
        semanas_cotizadas=request.semanas_cotizadas,
        periodos=request.periodos,
    )
    rpm_result = calcular_pension(rpm_input)
    
    rais_input = RaisInput(
        rentabilidad_anual=request.rentabilidad_esperada or 0.05,
        tipo_fondo=request.tipo_fondo or "Moderado",
        comision_afp=request.comision_afp or 0.015,
    )
    
    comparacion = comparar_regimenes(
        rpm_result, rais_input, request.periodos, 
        request.sexo, request.edad_jubilacion or 62
    )
    
    return comparacion
```

---

## 📊 Datos externos que necesitás cargar

### 1. Rentabilidad histórica por AFP y tipo de fondo
**Fuente:** Superintendencia Financiera de Colombia
**URL:** https://www.superfinanciera.gov.co/inicio/sala-de-prensa/boletines-/pensiones-/rentabilidad-de-los-fondos-de-pensiones-obligatorias-10594

**Formato esperado del JSON:**
```json
[
  {
    "afp": "Porvenir",
    "tipo_fondo": "Conservador",
    "rentabilidad_real_anual_promedio": 0.045,
    "ultima_actualizacion": "2026-06-30"
  }
]
```

### 2. Comisiones por AFP
**Fuente:** Superintendencia Financiera + cada AFP
**URL:** https://www.superfinanciera.gov.co

**Default conservador:** 1.5% sobre IBC

### 3. Tablas de mortalidad
**Fuente:** DANE (censo 2018 actualizado)
**URL:** https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion

**Para simplificar:** usar tabla estándar de mortalidad colombiana, asumir 20 años de retiro (240 meses) como default.

---

## 🛣️ Roadmap de implementación

| Semana | Tarea | Output |
|---|---|---|
| Sem 2 (post-deploy) | Implementar `RaisInput` + `proyectar_saldo_rais` + tests | Tests pasando |
| Sem 3 | Implementar `comparar_regimenes` + endpoint | Endpoint nuevo en `/docs` |
| Sem 3 | Cargar datos reales de rentabilidad desde SuperFinanciera | JSON con rentabilidades históricas |
| Sem 4 | Agregar UI en landing page: selector RPM vs RAIS vs ambos | Form actualizado |
| Sem 4 | Post Medium: "RPM vs RAIS: qué dice la matemática en 2026" | Article SEO |
| Sem 5 | Refinamiento: agregar más AFPs (Porvenir vs Protección vs Skandia) | Comparación multi-AFP |
| Mes 3+ | Integrar datos en tiempo real desde APIs públicas | Dashboard dinámico |

---

## ⚠️ Consideraciones importantes

### Limitaciones técnicas
- La rentabilidad futura NO es predecible. Asumimos 5% real anual pero puede ser 2% o 8%.
- Las comisiones de AFP cambian con el tiempo.
- El cálculo de mesada con tablas de mortalidad es complejo. Para un MVP, usar 240 meses es aceptable.

### Consideraciones regulatorias
- En Colombia, después de cumplir ciertos requisitos, el usuario puede **cambiar de RPM a RAIS o viceversa UNA SOLA VEZ** (restricción legal).
- Hay un régimen de transición para personas que estaban cotizando antes de 2004.
- La reforma pensional 2024 (Ley 2381) modifica requisitos para mujeres.

### Disclaimer legal obligatorio
```
Este cálculo es ESTIMATIVO y se basa en supuestos de rentabilidad futura,
comisiones actuales y tablas de mortalidad estándar. El monto real de su
pensión dependerá de múltiples factores no considerados en este modelo.
Consulte directamente con Colpensiones o su AFP para un cálculo oficial.
```

---

## 🎯 Resumen ejecutivo

**Para qué sirve esta extensión:**
- Comparar objetivamente RPM vs RAIS con datos reales del usuario
- Identificar cuál régimen da mejor pensión esperada en cada caso
- Educar al usuario sobre las diferencias (muchos colombianos no entienden)

**Cuándo implementarla:**
- Después del deploy público del MVP RPM (semana 1-2 del roadmap)
- Cuando ya tengas tracción inicial (semana 3-4)
- Antes de salir a marketing agresivo (semana 4)

**Complejidad estimada:**
- Módulo de cálculo: 1 semana (200-300 LOC Python + tests)
- Datos externos: 2-3 días (script de carga + JSON)
- Endpoint + UI: 2-3 días
- Total: **2 semanas** para tener comparación funcional

**Valor diferencial vs competencia:**
- Colpensiones solo calcula RPM
- Las AFPs solo calculan RAIS (con sesgo obvio)
- **Nadie en Colombia da comparación neutral matemática** ← esta es tu ventaja
