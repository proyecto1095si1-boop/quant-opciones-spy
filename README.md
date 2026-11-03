# Sistema de Inteligencia Cuantitativa de Opciones (SPY)

Plataforma de nodos que ingiere datos del S&P 500 (SPY), analiza price action y propone contratos de opciones.

> **Aviso**: proyecto educativo. Validar siempre en paper trading antes de usar dinero real. No es asesoría financiera.

## Estructura

```
quant-opciones-spy/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── opciones.py       # Descarga y filtrado de cadena de opciones
│   │   ├── price_action.py   # Velas OHLCV + patrones + sesgo (SMAs)
│   │   ├── signal.py         # Orquestador: bias → ticket de opción
│   │   └── main.py           # API FastAPI
│   └── requirements.txt
├── frontend/                 # React Flow (próximo)
├── .env.example
├── .gitignore
└── README.md
```

## Hoja de ruta

- [x] 1. Cadena de opciones filtrada
- [x] 2. API FastAPI (`/opciones`)
- [x] 3. Velas OHLCV + patrones de price action (engulfing, doji, hammer…)
- [x] 4. Sesgo con medias móviles + endpoint `/senal`
- [ ] 5. Lienzo visual React Flow
- [ ] 6. Letras griegas (Black-Scholes) + paper trading

## Cómo correr

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Probar módulos por separado
python -m app.opciones
python -c "from app.price_action import analizar; print(analizar('SPY'))"
python -c "from app.signal import generar_senal; print(generar_senal('SPY'))"

# Levantar la API
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Método | Ruta         | Descripción                                      |
|--------|--------------|--------------------------------------------------|
| GET    | `/`          | Info del proyecto                                |
| GET    | `/health`    | Health check                                     |
| GET    | `/opciones`  | Cadena de opciones filtrada                      |
| GET    | `/analisis`  | Price action: velas, patrones y sesgo            |
| GET    | `/senal`     | **Ticket completo**: bias → contrato recomendado |

### Ejemplo de señal

```bash
curl "http://localhost:8000/senal?ticker=SPY"
```

Respuesta (esquema):

```json
{
  "ticker": "SPY",
  "bias": "BEARISH",
  "accion": "COMPRAR",
  "tipo_opcion": "put",
  "justificacion": "Sesgo bajista → se buscan Puts OTM",
  "precio_subyacente": 752.10,
  "vencimiento": "2026-12-18",
  "dte": 45,
  "contrato_recomendado": {
    "symbol": "SPY261218P00750000",
    "strike": 750.0,
    "bid": 12.3,
    "ask": 12.6,
    "mid": 12.45,
    "spread_pct": 2.4,
    "iv": 0.18,
    "openInterest": 4200
  },
  "alternativas": [ ... ],
  "analisis": {
    "sesgo": { "bias": "BEARISH", "sma20": 769.3, "razones": [...] },
    "patrones": [],
    "velas_recientes": [ ... ]
  }
}
```

## Lógica del motor

1. **Price Action** (`price_action.py`)
   - Descarga OHLCV
   - Detecta: Bullish/Bearish Engulfing, Doji, Hammer, Shooting Star
   - Calcula sesgo con SMA20 / SMA50 + momentum 3-5 días

2. **Selección de derivado** (`signal.py`)
   - BULLISH → Calls OTM 30-45 DTE
   - BEARISH → Puts OTM 30-45 DTE
   - NEUTRAL → ESPERAR
   - Ranking por liquidez (OI) y spread estrecho

## Fuentes de datos

- **Desarrollo**: yfinance
- **Producción** (futuro): Alpaca, Tradier o Interactive Brokers
