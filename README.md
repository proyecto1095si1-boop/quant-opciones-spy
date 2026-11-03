# Sistema de Inteligencia Cuantitativa de Opciones (SPY)

Plataforma de nodos: price action → griegas Black-Scholes → ticket de opciones → **paper trading**.

> **Aviso**: proyecto educativo. Validar siempre en paper trading. No es asesoría financiera.

## Estructura

```
backend/app/
  opciones.py       # Cadena filtrada
  price_action.py   # Velas + patrones + SMAs
  greeks.py         # Black-Scholes
  signal.py         # Orquestador → ticket
  paper.py          # Journal paper (posiciones + PnL)
  main.py           # FastAPI
frontend/           # React Flow (Market → Quant → Signal)
backend/data/       # Journal JSON (gitignored)
```

## Hoja de ruta

- [x] 1–4 Backend (opciones, price action, sesgo, API)
- [x] 5 Lienzo React Flow
- [x] 6 Griegas Black-Scholes
- [x] 7 Paper trading (journal, abrir/cerrar, PnL)
- [ ] 8 Broker real (Alpaca / IB) — opcional

## Cómo correr

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

## Paper trading

| Endpoint | Descripción |
|----------|-------------|
| `GET /paper/estado` | Cash, PnL realizado, winrate |
| `GET /paper/posiciones` | Posiciones abiertas |
| `GET /paper/historial` | Trades cerrados |
| `POST /paper/abrir?ticker=SPY&qty=1` | Genera señal y abre si es COMPRAR |
| `POST /paper/abrir-manual` | Entrada manual |
| `POST /paper/cerrar?position_id=…&premium_salida=…` | Cierra y calcula PnL |
| `POST /paper/reset?cash=100000` | Reinicia account |

Cash inicial: **$100,000**. Cada contrato = prima × 100 × qty.

En el frontend, el nodo **Signal** tiene el botón **Abrir en paper** cuando hay señal de COMPRAR. El topbar muestra cash y PnL.

## Endpoints principales

`/opciones` · `/analisis` · `/senal` · `/greeks` · `/paper/*`

## Lógica del motor

1. Price action → bias  
2. Cadena OTM + liquidez  
3. Griegas (Delta 0.20–0.45, |Theta| acotado)  
4. Ranking → ticket  
5. Paper: abrir / cerrar / journal  
