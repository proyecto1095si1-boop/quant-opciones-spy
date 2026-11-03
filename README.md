# Sistema de Inteligencia Cuantitativa de Opciones (SPY)

Plataforma de nodos que ingiere datos del S&P 500 (SPY), analiza price action y propone contratos de opciones.

> **Aviso**: proyecto educativo. Validar siempre en paper trading antes de usar dinero real. No es asesoría financiera.

## Estructura

```
quant-opciones-spy/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── opciones.py      # Motor de descarga y filtrado de cadena
│   │   └── main.py          # API FastAPI
│   └── requirements.txt
├── frontend/                # React Flow (próximo)
├── .env.example
├── .gitignore
└── README.md
```

## Hoja de ruta

- [x] 1. Cadena de opciones filtrada (`backend/app/opciones.py`)
- [x] 2. API FastAPI (`/opciones`)
- [ ] 3. Velas OHLCV + patrones de price action (engulfing, doji…)
- [ ] 4. Sesgo con medias móviles
- [ ] 5. Lienzo visual React Flow
- [ ] 6. Letras griegas (Black-Scholes) + paper trading

## Cómo correr

### 1. Backend (API + script)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Probar el motor como script
python -m app.opciones

# Levantar la API
uvicorn app.main:app --reload --port 8000
```

Endpoints disponibles:

| Método | Ruta        | Descripción                          |
|--------|-------------|--------------------------------------|
| GET    | `/`         | Info del proyecto                    |
| GET    | `/health`   | Health check                         |
| GET    | `/opciones` | Cadena filtrada (parámetros opcionales) |

Ejemplo:

```bash
curl "http://localhost:8000/opciones?ticker=SPY&tipo=call&dte_min=30&dte_max=45"
```

Parámetros de `/opciones`:

- `ticker` (default: SPY)
- `tipo`: `call` | `put`
- `dte_min` / `dte_max` (días al vencimiento)
- `otm_max_pct` (% máximo fuera del dinero)
- `oi_min` (open interest mínimo)
- `spread_max_pct` (spread bid/ask máximo permitido)

### 2. Frontend (próximamente)

React + React Flow + Zustand.

## Fuentes de datos

- **Desarrollo**: yfinance
- **Producción** (futuro): Alpaca, Tradier o Interactive Brokers
