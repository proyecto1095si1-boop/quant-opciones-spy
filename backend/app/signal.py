"""
Orquestador: une price action + selección de opciones
y emite un ticket de señal listo para el nodo Signal.
"""

from __future__ import annotations

from typing import Any, Literal

from app.opciones import filtrar_cadena
from app.price_action import analizar


def generar_senal(
    ticker: str = "SPY",
    dte_min: int = 30,
    dte_max: int = 45,
    otm_max_pct: float = 5.0,
    oi_min: int = 200,
    spread_max_pct: float = 8.0,
) -> dict[str, Any]:
    """
    Pipeline completo:
    1. Analiza price action → bias
    2. Según bias elige call o put
    3. Filtra la cadena y selecciona el contrato más eficiente
    """
    analisis = analizar(ticker)
    bias = analisis["sesgo"]["bias"]

    if bias == "BULLISH":
        tipo: Literal["call", "put"] = "call"
        justificacion = "Sesgo alcista → se buscan Calls OTM"
    elif bias == "BEARISH":
        tipo = "put"
        justificacion = "Sesgo bajista → se buscan Puts OTM"
    else:
        # Neutral: no forzamos dirección
        return {
            "ticker": ticker,
            "bias": bias,
            "accion": "ESPERAR",
            "justificacion": "Sesgo NEUTRAL. No hay ventaja direccional clara.",
            "analisis": analisis,
            "contrato_recomendado": None,
            "alternativas": [],
        }

    cadena = filtrar_cadena(
        ticker=ticker,
        tipo=tipo,
        dte_min=dte_min,
        dte_max=dte_max,
        otm_max_pct=otm_max_pct,
        oi_min=oi_min,
        spread_max_pct=spread_max_pct,
    )

    contratos = cadena.get("contratos", [])

    if not contratos:
        return {
            "ticker": ticker,
            "bias": bias,
            "accion": "ESPERAR",
            "justificacion": (
                f"{justificacion}. Ningún contrato pasó los filtros de liquidez/spread. "
                "Relajar parámetros o esperar mejor setup."
            ),
            "analisis": analisis,
            "cadena": cadena,
            "contrato_recomendado": None,
            "alternativas": [],
        }

    # Ranking simple: preferir mayor OI y menor spread (liquidez)
    def score(c: dict) -> float:
        oi = c.get("openInterest") or 0
        spread = c.get("spread_pct") or 99
        return oi / 1000.0 - spread * 2

    ordenados = sorted(contratos, key=score, reverse=True)
    mejor = ordenados[0]
    alternativas = ordenados[1:4]

    return {
        "ticker": ticker,
        "bias": bias,
        "accion": "COMPRAR",
        "tipo_opcion": tipo,
        "justificacion": justificacion,
        "analisis": analisis,
        "vencimiento": cadena["vencimiento"],
        "dte": cadena["dte"],
        "precio_subyacente": cadena["precio"],
        "contrato_recomendado": {
            "symbol": mejor["contractSymbol"],
            "strike": mejor["strike"],
            "bid": mejor["bid"],
            "ask": mejor["ask"],
            "mid": round((mejor["bid"] + mejor["ask"]) / 2, 3),
            "spread_pct": mejor["spread_pct"],
            "iv": mejor.get("impliedVolatility"),
            "volume": mejor.get("volume"),
            "openInterest": mejor.get("openInterest"),
        },
        "alternativas": [
            {
                "symbol": c["contractSymbol"],
                "strike": c["strike"],
                "bid": c["bid"],
                "ask": c["ask"],
                "mid": round((c["bid"] + c["ask"]) / 2, 3),
                "spread_pct": c["spread_pct"],
                "openInterest": c.get("openInterest"),
            }
            for c in alternativas
        ],
    }
