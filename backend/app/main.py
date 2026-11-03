"""
API FastAPI del Sistema de Inteligencia Cuantitativa de Opciones.
"""

from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.greeks import black_scholes
from app.opciones import filtrar_cadena
from app.price_action import analizar
from app.signal import generar_senal

app = FastAPI(
    title="Quant Opciones SPY",
    description="Price action + griegas Black-Scholes + tickets de opciones para SPY",
    version="0.3.0",
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
        "version": "0.3.0",
        "endpoints": ["/health", "/opciones", "/analisis", "/senal", "/greeks"],
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.3.0"}


@app.get("/opciones")
def get_opciones(
    ticker: str = Query("SPY"),
    tipo: Literal["call", "put"] = Query("call"),
    dte_min: int = Query(30, ge=1, le=365),
    dte_max: int = Query(45, ge=1, le=365),
    otm_max_pct: float = Query(5.0, ge=0.5, le=30),
    oi_min: int = Query(200, ge=0),
    spread_max_pct: float = Query(8.0, ge=0.5, le=20),
):
    if dte_min > dte_max:
        raise HTTPException(status_code=400, detail="dte_min > dte_max")
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analisis")
def get_analisis(
    ticker: str = Query("SPY"),
    period: str = Query("3mo"),
    interval: str = Query("1d"),
):
    try:
        return analizar(ticker=ticker.upper(), period=period, interval=interval)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/senal")
def get_senal(
    ticker: str = Query("SPY"),
    dte_min: int = Query(30, ge=1, le=365),
    dte_max: int = Query(45, ge=1, le=365),
    otm_max_pct: float = Query(5.0, ge=0.5, le=30),
    oi_min: int = Query(200, ge=0),
    spread_max_pct: float = Query(8.0, ge=0.5, le=20),
    delta_min: Optional[float] = Query(0.20, ge=0.05, le=0.95),
    delta_max: Optional[float] = Query(0.45, ge=0.05, le=0.95),
    theta_max_abs: Optional[float] = Query(0.15, ge=0.01, le=5.0),
):
    if dte_min > dte_max:
        raise HTTPException(status_code=400, detail="dte_min > dte_max")
    try:
        return generar_senal(
            ticker=ticker.upper(),
            dte_min=dte_min,
            dte_max=dte_max,
            otm_max_pct=otm_max_pct,
            oi_min=oi_min,
            spread_max_pct=spread_max_pct,
            delta_min=delta_min,
            delta_max=delta_max,
            theta_max_abs=theta_max_abs,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando señal: {e}")


@app.get("/greeks")
def get_greeks(
    S: float = Query(..., description="Precio del subyacente"),
    K: float = Query(..., description="Strike"),
    dte: int = Query(..., ge=0, description="Días al vencimiento"),
    iv: float = Query(..., gt=0, description="Volatilidad implícita (decimal)"),
    tipo: Literal["call", "put"] = Query("call"),
    r: float = Query(0.045),
):
    T = max(dte, 0) / 365.0
    sigma = iv if iv <= 3 else iv / 100.0
    result = black_scholes(S=S, K=K, T=T, r=r, sigma=sigma, option_type=tipo)
    return {
        "inputs": {"S": S, "K": K, "dte": dte, "T_years": round(T, 4), "iv": sigma, "r": r, "tipo": tipo},
        "greeks": result,
    }
