# Sistema de Inteligencia Cuantitativa de Opciones (SPY)

Price action → griegas Black-Scholes → ticket → paper local → **Alpaca Paper** (opcional).

> Proyecto educativo. No es asesoría financiera.

## Lienzo

```
[Market] → [Quant Engine] → [Signal] → [Paper Journal]
```

## Cómo correr

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Opcional: copiá .env.example → .env y poné keys de Alpaca Paper
uvicorn app.main:app --reload --port 8000

cd frontend && npm install && npm run dev
```

## Paper local vs Alpaca

| | Paper local (`/paper/*`) | Alpaca Paper (`/broker/*`) |
|--|--------------------------|----------------------------|
| Keys | No | Sí (gratis en alpaca.markets) |
| Persistencia | `backend/data/paper_journal.json` | Cuenta Alpaca |
| Órdenes | Simuladas | Market/limit reales en paper |

```bash
# Estado broker
curl localhost:8000/broker/status

# Ordenar desde señal (requiere keys)
curl -X POST "localhost:8000/broker/ordenar?ticker=SPY&qty=1"
```

## API resumen

- `/analisis` · `/senal` · `/greeks`
- `/paper/estado` · `/paper/abrir` · `/paper/cerrar`
- `/broker/status` · `/broker/ordenar` · `/broker/positions`

## Stack

FastAPI + yfinance + Black-Scholes · React Flow + Zustand · Alpaca Paper (opcional)
