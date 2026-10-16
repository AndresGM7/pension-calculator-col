# Guía de Deploy - pension-calculator a Fly.io

## Pre-requisitos
- [x] Fly CLI instalado en `C:\Users\Andres Giraldo\.fly\bin\flyctl.exe`
- [ ] Cuenta Fly.io creada en https://fly.io/app/sign-up
- [ ] Tarjeta de crédito registrada (Fly pide aunque el plan free no cobre)
- [ ] Authenticated: `flyctl auth login`

## Paso 1: Autenticarse en Fly.io

```bash
"C:/Users/Andres Giraldo/.fly/bin/flyctl.exe" auth login
```

Esto abre el navegador para OAuth con GitHub o email.

## Paso 2: Crear la app en Fly

Desde el directorio del proyecto:
```bash
cd "C:/Users/Andres Giraldo/Projects/pension-calculator"
"C:/Users/Andres Giraldo/.fly/bin/flyctl.exe" launch --no-deploy
```

Esto crea la app `pension-calc-co` basada en el `fly.toml`. Como el flag es `--no-deploy`, no intenta deployar todavía.

## Paso 3: Generar secretos

```bash
# Generar SECRET_KEY y JWT_SECRET
"C:/Users/Andres Giraldo/.fly/bin/flyctl.exe" secrets set SECRET_KEY=*** --app pension-calc-co
"C:/Users/Andres Giraldo/.fly/bin/flyctl.exe" secrets set JWT_SECRET=*** --app pension-calc-co
```

(Reemplazar `***` por el output de `python -c "import secrets; print(secrets.token_urlsafe(64))"`)

## Paso 4: Deploy

```bash
"C:/Users/Andres Giraldo/.fly/bin/flyctl.exe" deploy
```

Esto:
1. Construye el Dockerfile
2. Sube la imagen a Fly
3. Despliega en la región `gru` (São Paulo)
4. Te da una URL: `https://pension-calc-co.fly.dev`

## Paso 5: Verificar

```bash
"C:/Users/Andres Giraldo/.fly/bin/flyctl.exe" open
```

O manualmente: https://pension-calc-co.fly.dev/health

Debería responder: `{"status": "ok", "version": "0.1.0"}`

## Paso 6: Deploy landing a Netlify

### Opción A: Drag & drop
1. Ir a https://app.netlify.com/drop
2. Arrastrar la carpeta `landing/` completa
3. Te da una URL `*.netlify.app`

### Opción B: Conectar a GitHub (más profesional)
1. Subir repo a GitHub (ver paso 7)
2. En Netlify, "Add new site" → "Import existing project" → seleccionar repo
3. Build settings:
   - Base directory: `landing`
   - Build command: (vacío)
   - Publish directory: `.`
4. Deploy

## Paso 7: Subir a GitHub

```bash
cd "C:/Users/Andres Giraldo/Projects/pension-calculator"

# Crear repo en GitHub primero (https://github.com/new)
# Nombre: pension-calculator
# NO inicializar con README (ya tenemos uno)

git remote add origin https://github.com/AndresGM7/pension-calculator.git
git branch -M main
git add .
git commit -m "feat: initial pension calculator with IPC indexation"
git push -u origin main
```

## Verificación final

Una vez deployed:
- [ ] API health check responde 200: https://pension-calc-co.fly.dev/health
- [ ] Swagger docs funcionan: https://pension-calc-co.fly.dev/docs
- [ ] Landing carga: https://mipension.co (o tu dominio Netlify)
- [ ] Form de landing llama API correctamente
- [ ] CORS permite requests desde Netlify (configurar en `.env` o fly secrets)

## Troubleshooting

### Error: "No access token available"
Hiciste `flyctl deploy` sin estar autenticado. Ejecutar `flyctl auth login` primero.

### Error: "App name already taken"
Cambiar `app = "pension-calc-co"` en `fly.toml` por otro nombre único.

### Error: "Image exceeds size limit"
Probablemente instalaste dev dependencies. Verificar que `pyproject.toml` solo tiene runtime deps.

### Error 502 Bad Gateway
El container crasheó. Ver logs: `flyctl logs --app pension-calc-co`

### CORS error desde landing
Agregar el dominio de Netlify a CORS allowed origins en `src/core/settings.py`.

## Costos estimados (plan free de Fly)

| Recurso | Costo mensual |
|---|---|
| 1 VM shared-cpu 512mb | $0 (incluido en free tier) |
| 3GB bandwidth | $0 |
| SSL | $0 |
| Total | **$0** mientras estés en free tier |

Cuando excedas free tier: ~$5-10/mes para este tamaño de app.
