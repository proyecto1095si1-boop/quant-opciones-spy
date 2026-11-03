"""
Backtest simple del sesgo de price action sobre velas históricas.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.price_action import calcular_sesgo, obtener_velas


def backtest_bias(
    ticker: str = "SPY",
    period: str = "6mo",
    horizon_days: int = 5,
    min_points: int = 2,
) -> dict[str, Any]:
    df = obtener_velas(ticker, period=period, interval="1d")
    if len(df) < 60:
        raise ValueError(f"Pocas velas para backtest ({len(df)})")

    rows = []
    for i in range(50, len(df) - horizon_days):
        window = df.iloc[: i + 1].copy()
        sesgo = calcular_sesgo(window)
        bias = sesgo["bias"]
        puntos = sesgo["puntos"]

        if abs(puntos) < min_points and bias == "NEUTRAL":
            continue

        px_now = float(df.iloc[i]["close"])
        px_fwd = float(df.iloc[i + horizon_days]["close"])
        ret = (px_fwd / px_now - 1.0) * 100.0

        if bias == "BULLISH":
            hit = ret > 0
            strategy_ret = ret
        elif bias == "BEARISH":
            hit = ret < 0
            strategy_ret = -ret
        else:
            continue

        rows.append(
            {
                "date": str(df.index[i])[:10],
                "bias": bias,
                "puntos": puntos,
                "precio": round(px_now, 2),
                "ret_fwd_pct": round(ret, 3),
                "strategy_ret_pct": round(strategy_ret, 3),
                "hit": hit,
            }
        )

    if not rows:
        return {
            "ticker": ticker,
            "period": period,
            "horizon_days": horizon_days,
            "trades": 0,
            "message": "Sin señales con los filtros actuales",
        }

    pdf = pd.DataFrame(rows)
    hits = int(pdf["hit"].sum())
    n = len(pdf)
    bull = pdf[pdf["bias"] == "BULLISH"]
    bear = pdf[pdf["bias"] == "BEARISH"]

    def _side_stats(side: pd.DataFrame) -> dict[str, Any]:
        if side.empty:
            return {"n": 0}
        return {
            "n": int(len(side)),
            "hitrate_pct": round(float(side["hit"].mean()) * 100, 1),
            "avg_ret_pct": round(float(side["ret_fwd_pct"].mean()), 3),
            "avg_strategy_ret_pct": round(float(side["strategy_ret_pct"].mean()), 3),
        }

    return {
        "ticker": ticker,
        "period": period,
        "horizon_days": horizon_days,
        "min_points": min_points,
        "trades": n,
        "hitrate_pct": round(hits / n * 100, 1),
        "avg_strategy_ret_pct": round(float(pdf["strategy_ret_pct"].mean()), 3),
        "median_strategy_ret_pct": round(float(pdf["strategy_ret_pct"].median()), 3),
        "bullish": _side_stats(bull),
        "bearish": _side_stats(bear),
        "ultimas_senales": rows[-10:],
    }
