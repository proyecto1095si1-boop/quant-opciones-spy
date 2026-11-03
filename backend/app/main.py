"""
API FastAPI del Sistema de Inteligencia Cuantitativa de Opciones.
"""

from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.opciones import filtrar_cadena

app = FastAPI(
    title="Quant Opciones SPY",
    description="Motor de datos y filtrado de cadena de opciones para SPY / S&P 500",
    version="0.1.0",
)

# Permitir el frontend React en desarrollo
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
        "version": "0.1.0",
        "endpoints": ["/opciones", "/health"],
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
    oi_min: int = Query(500, ge=0, description="Open Interest mínimo"),
    spread_max_pct: float = Query(5.0, ge=0.5, le=20, description="Spread máximo permitido (%)"),
):
    """
    Devuelve la cadena de opciones filtrada según los criterios de liquidez,
    DTE y distancia al dinero.
    """
    if dte_min > dte_max:
        raise HTTPException(status_code=400, detail="dte_min no puede ser mayor que dte_max")

    try:
        resultado = filtrar_cadena(
            ticker=ticker.upper(),
            tipo=tipo,
            dte_min=dte_min,
            dte_max=dte_max,
            otm_max_pct=otm_max_pct,
            oi_min=oi_min,
            spread_max_pct=spread_max_pct,
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")
