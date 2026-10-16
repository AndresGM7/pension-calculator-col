# Landing Page - pension-calculator (agnostica B2C+B2B)

Archivo: `landing/index.html`

## Estructura

### Hero
- Titulo universal: "Calcula tu pension en Colombia en 60 segundos"
- NO menciona solo B2C ni solo B2B
- Doble CTA: "Calcular gratis" (persona) + "Soy contador" (B2B)

### Pricing
- 4 planes visibles, no tiers verticales:
  1. **Gratis**: B2C anonimo, 3 calculos/dia
  2. **Reporte Unico $5**: B2C purchaser, pago unico
  3. **Contador Starter $29/mes**: B2B suscripcion basica, 5 perfiles
  4. **Contador Pro $99/mes**: B2B pro, 50 perfiles + alertas

### Seccion dual B2C/B2B
- Card izquierda: "Para tu pension personal" (tono B2C, ahorro, decision)
- Card derecha: "Para contadores y asesores" (tono B2B, multiples clientes, ROI)

### Conversion paths
- B2C ve reportes y calculos individuales
- B2B ve dashboard, multiples perfiles, herramientas para clientes
- Conversion natural: despues de 2 calculos B2C, sugerencia sutil a B2B

### Mensaje clave (subtitulo)
> "Para tu pension personal o para asesorar a tus clientes - el mismo motor profesional."

## Cambio vs version anterior

| Antes | Ahora |
|-------|-------|
| "Free / Premium $5 / Pro $15" | "Gratis / Reporte $5 / Starter $29-mes / Pro $99-mes" |
| Un solo tono (consumidor) | Dual: persona + contador |
| Tiers verticales | Modelo agnostico con modo autodetectado |
| Feature gates duros | Paywalls suaves con upgrade options |

## Conversion B2C -> B2B

Triggers automaticos (post-MVP):
- Despues de 2 compras de reporte unico: "Sos contador? El plan B2B te conviene mas."
- Despues de crear perfil: "Para guardar mas perfiles (familia), proba el plan B2B."
- En landing footer: link "Sos contador? Mira planes B2B aqui."

Estos mensajes son informativos, no agresivos. El usuario B2C que NO es contador no los ve como spam.
