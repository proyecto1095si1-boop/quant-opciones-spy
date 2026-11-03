# Sistema de Inteligencia Cuantitativa de Opciones (SPY)

Plataforma de nodos que ingiere datos del S&P 500 (SPY), analiza price action y propone contratos de opciones.

> **Aviso**: proyecto educativo. Validar siempre en paper trading antes de usar dinero real. No es asesoría financiera.

## Estructura

```
quant-opciones-spy/
├── backend/
│   ├── app/
│   │   ├── opciones.py       # Cadena de opciones filtrada
│   │   ├── price_action.py   # Velas + patrones + SMAs
│   │   ├── signal.py         # Orquestador → ticket
│   │   └── main.py           # FastAPI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── nodes/            # Market, Quant Engine, Signal
│   │   ├── api.js
│   │   ├── store.js          # Zustand
│   │   ├── App.jsx           # React Flow canvas
│   │   └── styles/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Hoja de ruta

- [x] 1. Cadena de opciones filtrada
- [x] 2. API FastAPI (`/opciones`)
- [x] 3. Velas OHLCV + patrones (engulfing, doji, hammer…)
- [x] 4. Sesgo con medias móviles + `/senal`
- [x] 5. Lienzo visual React Flow (3 nodos)
- [ ] 6. Letras griegas (Black-Scholes) + paper trading

## Cómo correr

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abrí http://localhost:5173

El frontend llama a `http://localhost:8000`. Si necesitás otra URL:

```bash
VITE_API_URL=http://tu-api:8000 npm run dev
```

## Flujo del lienzo

```
[Market]  ──►  [Quant Engine]  ──►  [Signal]
 ticker         price action          ticket
 timeframe      bias + patrones       contrato
                botón "Ejecutar"
```

1. **Market Node** — elegís ticker y temporalidad  
2. **Quant Engine** — al pulsar *Ejecutar análisis* llama a `/analisis` + `/senal`  
3. **Signal Node** — muestra bias, acción (COMPRAR / ESPERAR) y el contrato recomendado  

## Endpoints API

| Método | Ruta         | Descripción                          |
|--------|--------------|--------------------------------------|
| GET    | `/health`    | Health check                         |
| GET    | `/opciones`  | Cadena filtrada                      |
| GET    | `/analisis`  | Price action + sesgo                 |
| GET    | `/senal`     | Ticket completo (bias → contrato)    |

## Lógica del motor

1. **Price Action** — OHLCV, Engulfing / Doji / Hammer / Shooting Star, SMA20/SMA50 + momentum  
2. **Selección** — BULLISH→Calls OTM · BEARISH→Puts OTM · NEUTRAL→ESPERAR  
3. **Ranking** — mayor Open Interest + spread estrecho  

## Fuentes de datos

- Desarrollo: yfinance  
- Producción (futuro): Alpaca, Tradier o Interactive Brokers  
