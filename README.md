# Pension Calculator - Colombian Pension Microservice

A production-grade API for calculating Colombian pension estimates under **Ley 100/1993** and **Ley 797/2003**, with automatic IPC indexation using official Banco de la República data.

## Features

- **IPC-indexed IBL calculation** using official Colombian inflation data (1954-2026)
- **Ley 797/2003 vigente** with decreciente replacement rate by income level
- **FastAPI** REST API with Pydantic v2 validation
- **Multi-tenant ready** architecture
- **Complete test coverage** (9/9 tests passing)
- **Professional PDF reports** with scenario projections

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2 (async)
- **Data:** IPC series from Banco de la República (864 monthly observations)
- **Architecture:** Clean separation between motor, API, and services
- **Testing:** pytest with comprehensive edge case coverage
- **PDF:** WeasyPrint / Edge headless conversion

## Quick Start

```bash
# Install
python -m venv .venv
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
pip install -e ".[dev]"

# Run tests
pytest

# Start server
uvicorn src.api.main:app --reload
```

Visit `http://localhost:8000/docs` for Swagger UI.

## API Endpoints

### POST /api/v1/pension/calcular
Calculate monthly pension based on labor history.

**Request:**
```json
{
  "fecha_nacimiento": "1963-12-06",
  "sexo": "M",
  "semanas_cotizadas": 1289,
  "periodos": [
    {
      "fecha_inicio": "1984-08-28",
      "fecha_fin": "1985-01-16",
      "ibc": 14610
    }
  ]
}
```

**Response:**
```json
{
  "tiene_derecho": true,
  "semanas_cotizadas": 1289,
  "semanas_faltantes": 11,
  "edad_actual": 62,
  "edad_jubilacion": 62,
  "ibl_calculado": 18643675.0,
  "ventana_utilizada": "ultimos_10_anos",
  "tasa_reemplazo": 0.55,
  "mesada_pensional": 10254021.25,
  "regimen_aplicable": "LEY_797_2003"
}
```

### POST /api/v1/pension/proyectar
Project when the user will be eligible for pension.

### GET /api/v1/pension/info/regimenes
Get information about Colombian pension regimes.

## Legal Framework

### Ley 100 de 1993 (Original)
- **Edad:** 62 (hombres) / 57 (mujeres)
- **Semanas mínimas:** 1,000
- **Tasa:** 65% + 1.5% cada 50 semanas, máximo 80%

### Ley 797 de 2003 (Vigente)
- **Edad:** 62 (hombres) / 57 (mujeres)
- **Semanas mínimas:** 1,300
- **Tasa base:** **decreciente según ingreso** (55% - 65%)
- **Incremento:** +1.5% cada 50 semanas sobre 1,300
- **Tope máximo:** 80% del IBL

### Deciles de Ingreso y Tasa Base

| Rango IBC (vs SMLMV) | Tasa Base |
|----------------------|-----------|
| IBC <= 1 SMLMV | 65.0% |
| 1 < IBC <= 4 SMLMV | 60.0% - 65.0% (interpolado) |
| 4 < IBC <= 10 SMLMV | 55.0% - 60.0% (interpolado) |
| IBC > 10 SMLMV | 55.0% |

## IBL (Ingreso Base de Liquidación) - Indexación al IPC

El IBL se calcula actualizando cada IBC al valor presente usando el IPC del DANE/Banrep:

```
IBC_actualizado = IBC_historico × (IPC_referencia / IPC_periodo)

IBL = promedio(IBC_actualizados) de la ventana legal:
  - 1,300 a 1,800 semanas: últimos 10 años
  - 1,800 a 2,200 semanas: últimos 20 años
  - más de 2,200 semanas: toda la vida laboral
```

**Fuente del IPC:** Banco de la República, serie mensual julio 1954 - junio 2026 (864 observaciones, base 100 = diciembre 2018).

## Project Structure

```
pension-calculator/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   ├── schemas.py           # Pydantic v2 schemas
│   │   └── routes/
│   │       └── pension.py       # Endpoints
│   ├── core/
│   │   ├── settings.py
│   │   └── pension/
│   │       ├── calculator.py    # Motor de cálculo
│   │       ├── ibc.py           # Ingreso Base Cotización
│   │       ├── ibl.py           # Ingreso Base Liquidación
│   │       ├── ipc.py           # IPC indexer (Banrep data)
│   │       ├── legislacion.py   # Tasa de reemplazo Ley 797
│   │       └── tasas.py         # Tasas cotización histórica
│   └── services/
│       ├── pdf_generator.py     # Reporte HTML/PDF
│       └── reporte_profesional.py
├── tests/
│   ├── test_pension.py          # Tests del motor
│   └── test_francisco.py        # Test con caso real
├── docs/
│   ├── normativa.md             # Marco legal detallado
│   ├── AUDITORIA_FUENTES.md     # Validación de fuentes
│   ├── EVALUACION_EXHAUSTIVA.md # Lista de inputs/suuestos
│   └── STATUS.md                # Estado del proyecto
├── data/
│   └── IPC_Índice de Precios al Consumidor.csv  # NO versionado
└── pyproject.toml
```

## Testing

```bash
# Run all tests
pytest -v

# Test with real data
pytest tests/test_francisco.py -v -s
```

**Coverage:** 9/9 tests passing
- Motor de cálculo (Ley 100/1993 vs Ley 797/2003)
- Cálculo de IBL con/sin IPC
- Regímenes de transición
- Casos edge (hombres vs mujeres, diferentes edades)
- Validación con datos reales de Colpensiones

## Disclaimers Importantes

Este motor es un **prototipo educativo** y **NO es vinculante** con Colpensiones o cualquier administradora de pensiones. Para decisiones oficiales sobre su pensión, consulte directamente con la entidad administradora mediante un estudio personalizado de su historia laboral.

**Diferencias con el simulador oficial:**
- El simulador de Colpensiones aplica fórmulas internas que consideran variables adicionales (aportes simultáneos, régimen de transición, indemnizaciones, topes específicos)
- Los resultados pueden diferir entre este motor y el cálculo oficial

## Roadmap

- [ ] Multi-tenant authentication (JWT)
- [ ] Payment integration (Stripe + NOWPayments crypto)
- [ ] Landing page for direct consumer access
- [ ] PDF generation with native WeasyPrint
- [ ] Comparison tool: RPM vs RAIS regimes
- [ ] Indemnización sustitutiva calculator
- [ ] AI-powered advisory with RAG on Colombian pension law

## License

MIT

## Author

**Andrés Giraldo**
- Email: andresgiraldo1988@gmail.com
- LinkedIn: [linkedin.com/in/andgm](https://linkedin.com/in/andgm)
- GitHub: [github.com/AndresGM7](https://github.com/AndresGM7)
