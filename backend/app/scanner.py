"""
Scanner multi-ticker: analiza varios símbolos y rankea por fuerza de sesgo.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from app.price_action import analizar

DEFAULT_UNIVERSE = ["SPY", "QQQ", "IWM", "DIA", "XLF", "XLE", "GLD", "TLT"]


def _safe_analisis(ticker: str) -> dict[str, Any] | None:
    try:
        a = analizar(ticker)
        sesgo = a.get("sesgo") or {}
        return {
            "ticker": ticker,
            "bias": sesgo.get("bias"),
            "puntos": sesgo.get("puntos"),
            "precio": sesgo.get("precio"),
            "sma20": sesgo.get("sma20"),
            "sma50": sesgo.get("sma50"),
            "ret_3d_pct": sesgo.get("ret_3d_pct"),
            "ret_5d_pct": sesgo.get("ret_5d_pct"),
            "razones": sesgo.get("razones", [])[:3],
            "patrones": [
                {"patron": p.get("patron"), "direccion": p.get("direccion")}
                for p in (a.get("patrones") or [])[:3]
            ],
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def escanear(
    tickers: list[str] | None = None,
    max_workers: int = 6,
) -> dict[str, Any]:
    universe = [t.strip().upper() for t in (tickers or DEFAULT_UNIVERSE) if t.strip()]
    results: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {pool.submit(_safe_analisis, t): t for t in universe}
        for fut in as_completed(futs):
            row = fut.result()
            if row:
                results.append(row)

    ok = [r for r in results if "error" not in r]
    errs = [r for r in results if "error" in r]

    bullish = sorted(
        [r for r in ok if r.get("bias") == "BULLISH"],
        key=lambda x: x.get("puntos") or 0,
        reverse=True,
    )
    bearish = sorted(
        [r for r in ok if r.get("bias") == "BEARISH"],
        key=lambda x: abs(x.get("puntos") or 0),
        reverse=True,
    )
    neutral = [r for r in ok if r.get("bias") == "NEUTRAL"]

    return {
        "universe": universe,
        "total": len(universe),
        "bullish": bullish,
        "bearish": bearish,
        "neutral": neutral,
        "errors": errs,
        "top_long": bullish[:3],
        "top_short": bearish[:3],
    }
