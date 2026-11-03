# Sistema de Inteligencia Cuantitativa de Opciones (SPY)

Price action → griegas → ticket → paper → Alpaca → **scanner multi-ticker** → **backtest**.

> Proyecto educativo. No es asesoría financiera.

## Lienzo

```
[Market]  →  [Quant Engine]  →  [Signal]  →  [Paper Journal]
[Scanner]
```

## Cómo correr

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

cd frontend && npm install && npm run dev
```

## Nuevos endpoints (v0.6)

### Scanner
```bash
curl "http://localhost:8000/scanner?tickers=SPY,QQQ,IWM,DIA,XLF"
```

### Backtest
```bash
curl "http://localhost:8000/backtest?ticker=SPY&period=6mo&horizon_days=5"
```

## API

| Ruta | Uso |
|------|-----|
| `/analisis` `/senal` `/greeks` | Motor de una señal |
| `/scanner` | Universo multi-ticker |
| `/backtest` | Validación histórica del bias |
| `/paper/*` | Journal local |
| `/broker/*` | Alpaca Paper (opcional) |
