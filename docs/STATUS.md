# Estado del Proyecto — pension-calculator

**Última actualización:** 26 julio 2026

## ✅ Lo que está armado (MVP v0.1.0)

| Archivo | Líneas | Para qué sirve |
|---|---|---|
| `pyproject.toml` | 67 | Dependencias del proyecto (FastAPI, Pydantic, etc.) |
| `.gitignore` | 32 | Archivos que Git debe ignorar |
| `.env.example` | 24 | Template de variables de entorno |
| `README.md` | 30 | Quickstart del proyecto |
| `src/api/main.py` | 44 | App FastAPI + health check + root |
| `src/core/settings.py` | 64 | Configuración centralizada (Pydantic v2) |
| `src/core/pension/calculator.py` | 166 | **Motor de cálculo Ley 100/1993 + Ley 797/2003** |
| `src/api/schemas.py` | 65 | Schemas Pydantic para input/output |
| `src/api/routes/pension.py` | 40 | Endpoint `POST /api/v1/pension/calcular` |
| `tests/test_pension.py` | 110 | Tests del motor de cálculo |
| `docs/normativa.md` | 71 | Marco legal colombiano |

## 🎯 Cómo correrlo

```bash
cd "C:\Users\Andres Felipe Giraldo\Projects\pension-calculator"

# Crear virtualenv
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -e ".[dev]"

# Crear .env desde template
copy .env.example .env

# Correr tests
pytest -v

# Levantar servidor
uvicorn src.api.main:app --reload
```

Después ir a `http://localhost:8000/docs` para Swagger UI.

## 🧪 Probar el endpoint con curl

```bash
curl -X POST "http://localhost:8000/api/v1/pension/calcular" ^
  -H "Content-Type: application/json" ^
  -d "{\"fecha_nacimiento\":\"1960-01-15\",\"sexo\":\"M\",\"semanas_cotizadas\":1300,\"ibl_promedio\":3000000}"
```

## 📋 Próximos pasos (por prioridad)

### Esta semana (consolidar MVP)
- [ ] Validar contra la historia laboral de Andrés (test real)
- [ ] Descargar cotizaciones de Colpensiones para verificar
- [ ] Endpoint `GET /api/v1/pension/proyectar` (proyección a futuro)
- [ ] Endpoint `POST /api/v1/pension/comparar-regimenes`

### Próximas semanas (producción)
- [ ] PDF generation con WeasyPrint
- [ ] Multi-tenant + JWT
- [ ] Stripe integration (pagos USD)
- [ ] NOWPayments integration (crypto)
- [ ] Landing page + form

### Mes 2 (escala)
- [ ] Deploy a Fly.io
- [ ] Landing pública
- [ ] First paying client

## 📚 Conocimiento consolidado

- FastAPI + Pydantic v2 (estructura, schemas, endpoints)
- Multi-tenancy (patrón de `tax-ai`)
- Cálculo actuarial (Ley 797/2003 tabla oficial)
- Testing con pytest
- Estructura de proyecto Python production-ready
