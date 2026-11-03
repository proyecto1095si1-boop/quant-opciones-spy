"""
Griegas de opciones vía Black-Scholes (modelo europeo).

Calcula: precio teórico, Delta, Gamma, Theta, Vega, Rho.
Usa math.erf para la N(x) — sin dependencia extra de scipy.
"""

from __future__ import annotations

import math
from typing import Literal


def _norm_cdf(x: float) -> float:
    """CDF de la normal estándar N(0,1)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    """PDF de la normal estándar."""
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def black_scholes(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: Literal["call", "put"] = "call",
) -> dict[str, float]:
    """
    Black-Scholes para opción europea.

    Theta se expresa por día calendario (÷ 365).
    Vega se expresa por 1% de vol (÷ 100).
    """
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        intrinsic = max(S - K, 0.0) if option_type == "call" else max(K - S, 0.0)
        return {
            "price": round(intrinsic, 4),
            "delta": 1.0 if (option_type == "call" and S > K) else (-1.0 if (option_type == "put" and S < K) else 0.0),
            "gamma": 0.0,
            "theta": 0.0,
            "vega": 0.0,
            "rho": 0.0,
        }

    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    pdf_d1 = _norm_pdf(d1)
    cdf_d1 = _norm_cdf(d1)
    cdf_d2 = _norm_cdf(d2)
    cdf_m_d1 = _norm_cdf(-d1)
    cdf_m_d2 = _norm_cdf(-d2)

    discount = math.exp(-r * T)

    if option_type == "call":
        price = S * cdf_d1 - K * discount * cdf_d2
        delta = cdf_d1
        theta_year = (
            -(S * pdf_d1 * sigma) / (2 * sqrt_T)
            - r * K * discount * cdf_d2
        )
        rho = K * T * discount * cdf_d2
    else:
        price = K * discount * cdf_m_d2 - S * cdf_m_d1
        delta = cdf_d1 - 1.0
        theta_year = (
            -(S * pdf_d1 * sigma) / (2 * sqrt_T)
            + r * K * discount * cdf_m_d2
        )
        rho = -K * T * discount * cdf_m_d2

    gamma = pdf_d1 / (S * sigma * sqrt_T)
    vega_year = S * pdf_d1 * sqrt_T

    return {
        "price": round(price, 4),
        "delta": round(delta, 4),
        "gamma": round(gamma, 6),
        "theta": round(theta_year / 365.0, 4),
        "vega": round(vega_year / 100.0, 4),
        "rho": round(rho / 100.0, 4),
    }


def enriquecer_contrato(
    contrato: dict,
    S: float,
    dte: int,
    option_type: Literal["call", "put"],
    r: float = 0.045,
) -> dict:
    """Añade griegas BS a un contrato de la cadena."""
    K = float(contrato.get("strike") or 0)
    iv = contrato.get("impliedVolatility")
    if iv is None or iv <= 0:
        iv = 0.20
    if iv > 3:
        iv = iv / 100.0

    T = max(dte, 1) / 365.0
    greeks = black_scholes(S=S, K=K, T=T, r=r, sigma=iv, option_type=option_type)

    mid = None
    bid = contrato.get("bid")
    ask = contrato.get("ask")
    if bid is not None and ask is not None:
        mid = round((bid + ask) / 2, 3)

    return {
        **contrato,
        "mid": mid if mid is not None else contrato.get("mid"),
        "iv": round(iv, 4),
        "bs_price": greeks["price"],
        "delta": greeks["delta"],
        "gamma": greeks["gamma"],
        "theta": greeks["theta"],
        "vega": greeks["vega"],
        "rho": greeks["rho"],
    }


def filtrar_por_griegas(
    contratos: list[dict],
    delta_min: float | None = None,
    delta_max: float | None = None,
    theta_max_abs: float | None = None,
) -> list[dict]:
    """Filtra por rango de |Delta| y techo de |Theta|."""
    out = []
    for c in contratos:
        d = abs(c.get("delta") or 0)
        th = abs(c.get("theta") or 0)
        if delta_min is not None and d < delta_min:
            continue
        if delta_max is not None and d > delta_max:
            continue
        if theta_max_abs is not None and th > theta_max_abs:
            continue
        out.append(c)
    return out
