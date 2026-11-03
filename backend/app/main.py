"""
API FastAPI del Sistema de Inteligencia Cuantitativa de Opciones.
"""

from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.opciones import filtrar_cadena
from app.price_action import analizar
from app.signal import generar_senal

app = FastAPI(
    title="Quant Opciones SPY",
    description="Motor de price action + filtrado de cadena de opciones para SPY / S&P 500",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "proyecto": "Sistema de Inteligencia Cuantitativa de Opciones",
        "version": "0.2.0",
        "endpoints": ["/health", "/opciones", "/analisis", "/senal"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/opciones")
def get_opciones(
    ticker: str = Query("SPY", description="Ticker del subyacente"),
    tipo: Literal["call", "put"] = Query("call", description="Tipo de opción"),
    dte_min: int = Query(30, ge=1, le=365, description="Días mínimos al vencimiento"),
    dte_max: int = Query(45, ge=1, le=365, description="Días máximos al vencimiento"),
    otm_max_pct: float = Query(5.0, ge=0.5, le=30, description="% máximo OTM"),
    oi_min: int = Query(200, ge=0, description="Open Interest mínimo"),
    spread_max_pct: float = Query(8.0, ge=0.5, le=20, description="Spread máximo permitido (%)"),
):
    """Cadena de opciones filtrada (sin análisis de sesgo)."""
    if dte_min > dte_max:
        raise HTTPException(status_code=400, detail="dte_min no puede ser mayor que dte_max")

    try:
        return filtrar_cadena(
            ticker=ticker.upper(),
            tipo=tipo,
            dte_min=dte_min,
            dte_max=dte_max,
            otm_max_pct=otm_max_pct,
            oi_min=oi_min,
            spread_max_pct=spread_max_pct,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")


@app.get("/analisis")
def get_analisis(
    ticker: str = Query("SPY", description="Ticker del subyacente"),
    period: str = Query("3mo", description="Periodo de velas (1mo, 3mo, 6mo…)"),
    interval: str = Query("1d", description="Temporalidad (1d, 1h, etc.)"),
):
    """
    Price action: velas recientes, patrones (engulfing, doji, hammer…)
    y sesgo BULLISH / BEARISH / NEUTRAL con SMAs.
    """
    try:
        return analizar(ticker=ticker.upper(), period=period, interval=interval)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")


@app.get("/senal")
def get_senal(
    ticker: str = Query("SPY", description="Ticker del subyacente"),
    dte_min: int = Query(30, ge=1, le=365),
    dte_max: int = Query(45, ge=1, le=365),
    otm_max_pct: float = Query(5.0, ge=0.5, le=30),
    oi_min: int = Query(200, ge=0),
    spread_max_pct: float = Query(8.0, ge=0.5, le=20),
):
    """
    Señal completa (ticket):
    1. Analiza price action → bias
    2. Elige Call o Put según bias
    3. Filtra y recomienda el contrato más líquido
    """
    if dte_min > dte_max:
        raise HTTPException(status_code=400, detail="dte_min no puede ser mayor que dte_max")

    try:
        return generar_senal(
            ticker=ticker.upper(),
            dte_min=dte_min,
            dte_max=dte_max,
            otm_max_pct=otm_max_pct,
            oi_min=oi_min,
            spread_max_pct=spread_max_pct,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando señal: {str(e)}")
