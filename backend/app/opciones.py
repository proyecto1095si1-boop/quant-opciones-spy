"""
Motor de datos y filtrado de la cadena de opciones de SPY (y otros tickers).

Uso como script:
    python -m app.opciones

Uso como módulo (desde FastAPI u otros):
    from app.opciones import filtrar_cadena
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import pandas as pd
import yfinance as yf

# ---- Parámetros por defecto ----
DEFAULTS = {
    "ticker": "SPY",
    "tipo": "call",  # "call" | "put"
    "dte_min": 30,
    "dte_max": 45,
    "otm_max_pct": 5.0,
    "oi_min": 500,
    "spread_max_pct": 5.0,
}


def obtener_precio(ticker: str) -> float:
    """Devuelve el último precio de cierre del subyacente."""
    activo = yf.Ticker(ticker)
    hist = activo.history(period="1d")
    if hist.empty:
        raise ValueError(f"No se pudo obtener precio para {ticker}")
    return float(hist["Close"].iloc[-1])


def elegir_vencimiento(
    ticker: str,
    dte_min: int = 30,
    dte_max: int = 45,
) -> tuple[str, int]:
    """
    Busca el primer vencimiento cuyo DTE esté en [dte_min, dte_max].
    Retorna (fecha_str, dte).
    """
    activo = yf.Ticker(ticker)
    hoy = datetime.now().date()
    for exp in activo.options:
        dte = (datetime.strptime(exp, "%Y-%m-%d").date() - hoy).days
        if dte_min <= dte <= dte_max:
            return exp, dte
    raise ValueError(f"No hay vencimientos entre {dte_min} y {dte_max} días para {ticker}")


def filtrar_cadena(
    ticker: str = "SPY",
    tipo: Literal["call", "put"] = "call",
    dte_min: int = 30,
    dte_max: int = 45,
    otm_max_pct: float = 5.0,
    oi_min: int = 500,
    spread_max_pct: float = 5.0,
) -> dict:
    """
    Descarga y filtra la cadena de opciones.

    Retorna un dict listo para serializar a JSON:
    {
        "ticker": ...,
        "precio": ...,
        "vencimiento": ...,
        "dte": ...,
        "tipo": ...,
        "contratos": [ {contractSymbol, strike, bid, ask, ...}, ... ]
    }
    """
    precio = obtener_precio(ticker)
    exp, dte = elegir_vencimiento(ticker, dte_min, dte_max)

    activo = yf.Ticker(ticker)
    cadena = activo.option_chain(exp)
    df = (cadena.calls if tipo == "call" else cadena.puts).copy()

    # Filtro OTM
    if tipo == "call":
        df = df[(df["strike"] > precio) & (df["strike"] <= precio * (1 + otm_max_pct / 100))]
    else:
        df = df[(df["strike"] < precio) & (df["strike"] >= precio * (1 - otm_max_pct / 100))]

    # Liquidez y cotización válida
    df = df[(df["bid"] > 0) & (df["ask"] > 0) & (df["openInterest"] >= oi_min)]

    # Spread
    df = df.copy()
    df["precio_medio"] = (df["bid"] + df["ask"]) / 2
    df["spread_pct"] = (df["ask"] - df["bid"]) / df["precio_medio"] * 100
    df = df[df["spread_pct"] <= spread_max_pct]

    if df.empty:
        return {
            "ticker": ticker,
            "precio": round(precio, 2),
            "vencimiento": exp,
            "dte": dte,
            "tipo": tipo,
            "contratos": [],
            "mensaje": "Ningún contrato pasó los filtros. Prueba relajar parámetros.",
        }

    columnas = [
        "contractSymbol",
        "strike",
        "bid",
        "ask",
        "spread_pct",
        "impliedVolatility",
        "volume",
        "openInterest",
    ]
    contratos = (
        df[columnas]
        .round({"strike": 2, "bid": 3, "ask": 3, "spread_pct": 2, "impliedVolatility": 4})
        .to_dict(orient="records")
    )

    return {
        "ticker": ticker,
        "precio": round(precio, 2),
        "vencimiento": exp,
        "dte": dte,
        "tipo": tipo,
        "contratos": contratos,
    }


def main():
    resultado = filtrar_cadena()
    print(f"{resultado['ticker']} precio: {resultado['precio']}")
    print(f"Vencimiento: {resultado['vencimiento']} ({resultado['dte']} días)\n")

    if not resultado["contratos"]:
        print(resultado.get("mensaje", "Sin contratos"))
        return

    df = pd.DataFrame(resultado["contratos"])
    pd.set_option("display.width", 200)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
