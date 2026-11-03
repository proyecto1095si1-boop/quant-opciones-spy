"""
Orquestador: une price action + selección de opciones + griegas
y emite un ticket de señal listo para el nodo Signal.
"""

from __future__ import annotations

from typing import Any, Literal

from app.greeks import enriquecer_contrato, filtrar_por_griegas
from app.opciones import filtrar_cadena
from app.price_action import analizar


def generar_senal(
    ticker: str = "SPY",
    dte_min: int = 30,
    dte_max: int = 45,
    otm_max_pct: float = 5.0,
    oi_min: int = 200,
    spread_max_pct: float = 8.0,
    delta_min: float | None = 0.20,
    delta_max: float | None = 0.45,
    theta_max_abs: float | None = 0.15,
    r: float = 0.045,
) -> dict[str, Any]:
    """
    Pipeline completo:
    1. Analiza price action → bias
    2. Según bias elige call o put
    3. Filtra la cadena (liquidez / spread / OTM)
    4. Calcula griegas BS y filtra por Delta / Theta
    5. Rankea y recomienda el mejor contrato
    """
    analisis = analizar(ticker)
    bias = analisis["sesgo"]["bias"]

    if bias == "BULLISH":
        tipo: Literal["call", "put"] = "call"
        justificacion = "Sesgo alcista → Calls OTM con Delta moderado"
    elif bias == "BEARISH":
        tipo = "put"
        justificacion = "Sesgo bajista → Puts OTM con Delta moderado"
    else:
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

    contratos_raw = cadena.get("contratos", [])
    S = cadena.get("precio") or analisis["sesgo"]["precio"]
    dte = cadena.get("dte") or 30

    if not contratos_raw:
        return {
            "ticker": ticker,
            "bias": bias,
            "accion": "ESPERAR",
            "justificacion": (
                f"{justificacion}. Ningún contrato pasó los filtros de liquidez/spread."
            ),
            "analisis": analisis,
            "cadena": cadena,
            "contrato_recomendado": None,
            "alternativas": [],
        }

    enriquecidos = [
        enriquecer_contrato(c, S=S, dte=dte, option_type=tipo, r=r)
        for c in contratos_raw
    ]

    filtrados = filtrar_por_griegas(
        enriquecidos,
        delta_min=delta_min,
        delta_max=delta_max,
        theta_max_abs=theta_max_abs,
    )

    pool = filtrados if filtrados else enriquecidos

    def score(c: dict) -> float:
        oi = c.get("openInterest") or 0
        spread = c.get("spread_pct") or 99
        delta = abs(c.get("delta") or 0)
        theta = abs(c.get("theta") or 0)
        delta_score = 1.0 - abs(delta - 0.30) * 2
        return (oi / 1000.0) + delta_score * 2 - spread * 1.5 - theta * 5

    ordenados = sorted(pool, key=score, reverse=True)
    mejor = ordenados[0]
    alternativas = ordenados[1:4]

    def _ticket(c: dict) -> dict:
        return {
            "symbol": c.get("contractSymbol") or c.get("symbol"),
            "strike": c.get("strike"),
            "bid": c.get("bid"),
            "ask": c.get("ask"),
            "mid": c.get("mid") or round(((c.get("bid") or 0) + (c.get("ask") or 0)) / 2, 3),
            "spread_pct": c.get("spread_pct"),
            "iv": c.get("iv") or c.get("impliedVolatility"),
            "volume": c.get("volume"),
            "openInterest": c.get("openInterest"),
            "delta": c.get("delta"),
            "gamma": c.get("gamma"),
            "theta": c.get("theta"),
            "vega": c.get("vega"),
            "bs_price": c.get("bs_price"),
        }

    filtro_griegas_activo = bool(filtrados)
    extra = ""
    if filtro_griegas_activo:
        extra = f" | Delta {delta_min}–{delta_max}, |Theta|≤{theta_max_abs}"
    else:
        extra = " | Filtro griegas relajado (pocos contratos líquidos)"

    return {
        "ticker": ticker,
        "bias": bias,
        "accion": "COMPRAR",
        "tipo_opcion": tipo,
        "justificacion": justificacion + extra,
        "analisis": analisis,
        "vencimiento": cadena["vencimiento"],
        "dte": cadena["dte"],
        "precio_subyacente": S,
        "filtros_griegas": {
            "delta_min": delta_min,
            "delta_max": delta_max,
            "theta_max_abs": theta_max_abs,
            "aplicado": filtro_griegas_activo,
            "candidatos_pre": len(enriquecidos),
            "candidatos_post": len(filtrados),
        },
        "contrato_recomendado": _ticket(mejor),
        "alternativas": [_ticket(c) for c in alternativas],
    }
