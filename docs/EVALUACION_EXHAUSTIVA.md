# Evaluación Exhaustiva — pension-calculator

## Inputs que NECESITO para calcular correctamente

### ✅ Datos que SÍ salen del PDF de Colpensiones

| Input | Dato | En nuestro motor |
|-------|------|-----------------|
| Identificación | CC 71647133 | OK (no usamos para cálculo) |
| Nombre | Francisco Giraldo | OK (no usamos) |
| Fecha nacimiento | 06/12/1963 | OK (campo fecha_nacimiento) |
| Sexo | M | OK (campo sexo) |
| Total semanas cotizadas | 1,289 | OK (campo semanas_cotizadas) |
| IBC por periodo | múltiples valores | OK (lista periodos) |
| Cotización pagada | múltiples valores | OK (no usamos para IBL) |
| Empleadores | múltiples | OK (no usamos para cálculo) |

### ⚠️ Datos que NECESITAMOS PERO NO TENEMOS

| Input | De dónde sale | Criticidad |
|-------|--------------|------------|
| **IPC histórico mensual** | DANE/Banrep | CRÍTICA — sin esto subestimamos |
| **Tabla tasa reemplazo OFICIAL** | Ley 797/2003 Art. 10 | CRÍTICA — la tabla actual puede estar mal |
| **Salario mínimo legal histórico** | Mintrabajo | MEDIA — para topes |
| **Rentabilidad fondos AFP** | SuperFinanciera | BAJA — solo RAIS |
| **Topes legales IBL** | Ley/Decretos | MEDIA — 1-25 SMLMV |
| **Tablas de mortalidad** | SuperFinanciera | BAJA — solo invalidez |

## Cálculos que HACEMOS (con suposiciones)

### 1. Tasa de reemplazo
- **Lo que asumimos:** Tabla de 23 tramos, 40%-80%
- **Realidad:** Ley dice 65% base + 2% cada 50 semanas, hasta 80%
- **Necesitamos verificar:** Si la tabla de 650 semanas viene de régimen de transición o es error
- **Impacto:** En Francisco (1,289 semanas, no califica), NO AFECTA — porque la tasa que se muestra es la proyectada a 1,300

### 2. IBL (Ingreso Base de Liquidación)
- **Lo que hacemos:** Promedio simple de IBC en ventana
- **Lo que deberíamos hacer:** Promedio INDEXADO al IPC
- **Impacto:** Para 40 años de historia, el IPC acumulado es ENORME (~5000% en Colombia)
- **Sin indexación:** Estamos SUBESTIMANDO la pensión

### 3. Edad de jubilación
- **Ley:** 62 hombres, 57 mujeres
- **Ley 2381/2024 (reforma Petro):** Modifica para mujeres — 1 año menos cada cierto tiempo hasta llegar a 50
- **Lo que hacemos:** Hardcodeado 62/57
- **Necesitamos:** Validar la transición que está vigente en 2026

### 4. Topes legales
- **Ley:** IBL entre 1 SMLMV y 25 SMLMV
- **Lo que hacemos:** No validamos
- **Francisco:** IBL = $17.6M, ~10 SMLMV (cumple)
- **Impacto:** Bajo en Francisco, alto en personas de mayores ingresos

### 5. Régimen de transición
- **Lo que es:** Personas que cumplieron requisitos antes de Ley 797/2003 siguen con reglas antiguas
- **Lo que hacemos:** No manejamos transición
- **Para Francisco:** Nació 1963, empezó 1984. Cuando entró Ley 797 (2003), tenía 39 años y llevaba cotizando ~19 años. NO califica para transición (necesitaba tener 40 años hombre al entrar).
- **Pero otros usuarios sí podrían calificar**

## ¿Qué cambia si lo arreglamos BIEN?

### Impacto de indexar al IPC

Para Francisco con la tabla de IBC del PDF:
- 1984: $14.610
- 2025: $19.829.529

Si indexamos el IBC de 1984 al IPC de 2025:
- Inflación acumulada 1984-2025 en Colombia: ~12,000% (factor ~120x)
- IBC actualizado de 1984: $14.610 × 120 = $1,753,200

Eso SUBE el IBL significativamente porque los periodos antiguos valen más.

**Estimación:**
- IBL actual (sin indexar): $17.6M
- IBL indexado al IPC: ~$22-25M (estimación preliminar)
- Mesada a 80% (si llegara a 1,700 semanas): $20M vs $14M
- **Diferencia: +$6M/mes, +$72M/año**

**Eso es POR QUÉ importa indexar al IPC.**

## Plan de mejoras (en orden)

### Corto plazo (esta sesión)
1. [ ] Verificar tabla tasa de reemplazo contra Ley 797/2003
2. [ ] Investigar fuente de IPC (DANE API vs CSV)
3. [ ] Documentar TODAS las suposiciones

### Mediano plazo (próxima semana)
4. [ ] Descargar CSV de IPC del DANE
5. [ ] Implementar indexación al IPC
6. [ ] Agregar validación contra topes
7. [ ] Test con Francisco recalculado

### Largo plazo (cuando esté más maduro)
8. [ ] Manejar régimen de transición
9. [ ] Agregar soporte Ley 2381/2024
10. [ ] Certificación legal/abogada

## Riesgo legal

**IMPORTANTE:** Este motor NO es un sustituto de Colpensiones/AFP. Cualquier cálculo es ESTIMATIVO. Para uso oficial, hay que ir a la entidad.

**Disclaimer recomendado en el reporte final:**
> "Cálculo estimativo con fines educativos. El cálculo oficial lo realiza Colpensiones o su AFP según la normatividad vigente. Este documento NO constituye asesoría legal ni financiera."
