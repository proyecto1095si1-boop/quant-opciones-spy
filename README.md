# Sistema de Inteligencia Cuantitativa de Opciones (SPY)

Plataforma de nodos que ingiere datos del S&P 500 (SPY), analiza price action, calcula griegas Black-Scholes y propone contratos de opciones.

> **Aviso**: proyecto educativo. Validar siempre en paper trading. No es asesoría financiera.

## Estructura

```
quant-opciones-spy/
├── backend/app/
│   ├── opciones.py       # Cadena de opciones filtrada
│   ├── price_action.py   # Velas + patrones + SMAs
│   ├── greeks.py         # Black-Scholes (Delta, Theta, Gamma, Vega)
│   ├── signal.py         # Orquestador → ticket
│   └── main.py           # FastAPI
└── frontend/             # React Flow (Market → Quant → Signal)
```

## Hoja de ruta

- [x] 1. Cadena de opciones filtrada
- [x] 2. API FastAPI
- [x] 3. Velas OHLCV + patrones
- [x] 4. Sesgo con medias móviles
- [x] 5. Lienzo React Flow
- [x] 6. Letras griegas (Black-Scholes) + filtros Delta/Theta
- [ ] 7. Paper trading / broker connect

## Cómo correr

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

## Endpoints

| Ruta | Descripción |
|------|-------------|
| `/opciones` | Cadena filtrada |
| `/analisis` | Price action + sesgo |
| `/senal` | **Ticket**: bias → contrato + griegas |
| `/greeks` | Calculadora BS standalone (`S`, `K`, `dte`, `iv`, `tipo`) |

### Filtros de griegas en `/senal`

- `delta_min` / `delta_max` (default 0.20–0.45): zona OTM con probabilidad razonable
- `theta_max_abs` (default 0.15): techo de decaimiento diario

### Ejemplo calculadora

```bash
curl "http://localhost:8000/greeks?S=752&K=760&dte=35&iv=0.18&tipo=put"
```

## Lógica del motor

1. **Price Action** → bias BULLISH / BEARISH / NEUTRAL  
2. **Cadena** → OTM, liquidez, spread  
3. **Griegas BS** → Delta, Theta, Gamma, Vega  
4. **Filtro** → Delta 0.20–0.45, |Theta| acotado  
5. **Ranking** → OI alto + Delta ~0.30 + spread bajo  

## Frontend

Nodo **Signal** muestra Delta, Theta, Gamma y Vega del contrato recomendado.
