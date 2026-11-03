# Sistema de Inteligencia Cuantitativa de Opciones (SPY)

Plataforma de nodos: price action → griegas Black-Scholes → ticket → **paper trading**.

> **Aviso**: proyecto educativo. No es asesoría financiera.

## Lienzo (4 nodos)

```
[Market] → [Quant Engine] → [Signal] → [Paper Journal]
 ticker      bias + patrones    ticket + griegas   posiciones / PnL
             Ejecutar análisis  Abrir en paper     cerrar / reset
```

## Cómo correr

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

## API

| Ruta | Uso |
|------|-----|
| `/analisis` | Price action + sesgo |
| `/senal` | Ticket + griegas (Delta/Theta) |
| `/greeks` | Calculadora BS |
| `/paper/estado` | Cash, PnL, winrate |
| `/paper/abrir` | Abre desde señal |
| `/paper/cerrar` | Cierra con prima de salida |
| `/paper/reset` | Reinicia account |

Cash paper inicial: **$100,000**.

## Stack

Python + FastAPI + yfinance · React Flow + Zustand · Black-Scholes propio
