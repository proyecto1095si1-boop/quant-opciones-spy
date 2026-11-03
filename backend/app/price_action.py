"""
Análisis de price action: velas OHLCV, patrones de alta probabilidad
y definición de sesgo (BULLISH / BEARISH / NEUTRAL).
"""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd
import yfinance as yf

Bias = Literal["BULLISH", "BEARISH", "NEUTRAL"]


def obtener_velas(
    ticker: str = "SPY",
    period: str = "3mo",
    interval: str = "1d",
) -> pd.DataFrame:
    """Descarga OHLCV limpio (sin dividends/splits)."""
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    if df.empty or len(df) < 30:
        raise ValueError(f"No hay suficientes velas para {ticker}")
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.dropna()
    return df


def _cuerpo(row: pd.Series) -> float:
    return abs(row["close"] - row["open"])


def _rango(row: pd.Series) -> float:
    return row["high"] - row["low"]


def detectar_patrones(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Detecta patrones en las últimas velas.
    Devuelve lista de dicts con tipo, dirección y barra (índice relativo).
    """
    patrones: list[dict[str, Any]] = []
    if len(df) < 3:
        return patrones

    # Trabajamos con las últimas 5 velas para señales recientes
    ventana = df.tail(6).reset_index(drop=True)

    for i in range(1, len(ventana)):
        prev = ventana.iloc[i - 1]
        curr = ventana.iloc[i]
        cuerpo_prev = _cuerpo(prev)
        cuerpo_curr = _cuerpo(curr)
        rango_curr = _rango(curr) or 1e-9

        # --- Doji (indecisión) ---
        if cuerpo_curr / rango_curr < 0.12:
            patrones.append(
                {
                    "patron": "doji",
                    "direccion": "neutral",
                    "barra": i - (len(ventana) - 1),  # 0 = última vela
                    "descripcion": "Doji de indecisión",
                }
            )

        # --- Bullish Engulfing ---
        if (
            prev["close"] < prev["open"]  # previa bajista
            and curr["close"] > curr["open"]  # actual alcista
            and curr["open"] <= prev["close"]
            and curr["close"] >= prev["open"]
            and cuerpo_curr > cuerpo_prev * 1.1
        ):
            patrones.append(
                {
                    "patron": "bullish_engulfing",
                    "direccion": "bullish",
                    "barra": i - (len(ventana) - 1),
                    "descripcion": "Engulfing alcista",
                }
            )

        # --- Bearish Engulfing ---
        if (
            prev["close"] > prev["open"]
            and curr["close"] < curr["open"]
            and curr["open"] >= prev["close"]
            and curr["close"] <= prev["open"]
            and cuerpo_curr > cuerpo_prev * 1.1
        ):
            patrones.append(
                {
                    "patron": "bearish_engulfing",
                    "direccion": "bearish",
                    "barra": i - (len(ventana) - 1),
                    "descripcion": "Engulfing bajista",
                }
            )

        # --- Hammer / Shooting Star (rechazo) ---
        sombra_inf = min(curr["open"], curr["close"]) - curr["low"]
        sombra_sup = curr["high"] - max(curr["open"], curr["close"])
        cuerpo = cuerpo_curr or 1e-9

        if sombra_inf > cuerpo * 2 and sombra_sup < cuerpo * 0.5:
            patrones.append(
                {
                    "patron": "hammer",
                    "direccion": "bullish",
                    "barra": i - (len(ventana) - 1),
                    "descripcion": "Hammer (rechazo de mínimos)",
                }
            )
        if sombra_sup > cuerpo * 2 and sombra_inf < cuerpo * 0.5:
            patrones.append(
                {
                    "patron": "shooting_star",
                    "direccion": "bearish",
                    "barra": i - (len(ventana) - 1),
                    "descripcion": "Shooting Star (rechazo de máximos)",
                }
            )

    # Solo nos interesan patrones de las últimas 2-3 velas
    recientes = [p for p in patrones if p["barra"] >= -2]
    return recientes


def calcular_sesgo(df: pd.DataFrame) -> dict[str, Any]:
    """
    Cruza tendencia (SMAs) con momentum de precio reciente.
    Retorna bias + detalles de las medias.
    """
    df = df.copy()
    df["sma20"] = df["close"].rolling(20).mean()
    df["sma50"] = df["close"].rolling(50).mean()

    ultima = df.iloc[-1]
    prev = df.iloc[-2]

    precio = float(ultima["close"])
    sma20 = float(ultima["sma20"]) if pd.notna(ultima["sma20"]) else None
    sma50 = float(ultima["sma50"]) if pd.notna(ultima["sma50"]) else None

    # Momentum de las últimas 3-5 velas
    ret_3 = (precio / float(df.iloc[-4]["close"]) - 1) * 100 if len(df) >= 4 else 0.0
    ret_5 = (precio / float(df.iloc[-6]["close"]) - 1) * 100 if len(df) >= 6 else 0.0

    # Reglas simples y transparentes
    puntos = 0
    razones: list[str] = []

    if sma20 is not None and sma50 is not None:
        if precio > sma20 > sma50:
            puntos += 2
            razones.append("Precio > SMA20 > SMA50 (tendencia alcista)")
        elif precio < sma20 < sma50:
            puntos -= 2
            razones.append("Precio < SMA20 < SMA50 (tendencia bajista)")
        elif precio > sma20:
            puntos += 1
            razones.append("Precio por encima de SMA20")
        elif precio < sma20:
            puntos -= 1
            razones.append("Precio por debajo de SMA20")

        # Cruce reciente
        if prev["sma20"] <= prev["sma50"] and sma20 > sma50:
            puntos += 1
            razones.append("Cruce alcista SMA20/SMA50")
        elif prev["sma20"] >= prev["sma50"] and sma20 < sma50:
            puntos -= 1
            razones.append("Cruce bajista SMA20/SMA50")

    if ret_3 > 1.0:
        puntos += 1
        razones.append(f"Momentum 3 días positivo ({ret_3:.1f}%)")
    elif ret_3 < -1.0:
        puntos -= 1
        razones.append(f"Momentum 3 días negativo ({ret_3:.1f}%)")

    if puntos >= 2:
        bias: Bias = "BULLISH"
    elif puntos <= -2:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"

    return {
        "bias": bias,
        "puntos": puntos,
        "precio": round(precio, 2),
        "sma20": round(sma20, 2) if sma20 is not None else None,
        "sma50": round(sma50, 2) if sma50 is not None else None,
        "ret_3d_pct": round(ret_3, 2),
        "ret_5d_pct": round(ret_5, 2),
        "razones": razones,
    }


def analizar(
    ticker: str = "SPY",
    period: str = "3mo",
    interval: str = "1d",
) -> dict[str, Any]:
    """
    Pipeline completo de price action:
    velas → patrones → sesgo.
    """
    df = obtener_velas(ticker, period, interval)
    patrones = detectar_patrones(df)
    sesgo = calcular_sesgo(df)

    # Ajuste fino del bias según patrones muy recientes
    patrones_ultimos = [p for p in patrones if p["barra"] == 0]
    if patrones_ultimos:
        dirs = {p["direccion"] for p in patrones_ultimos}
        if "bullish" in dirs and sesgo["bias"] != "BEARISH":
            if sesgo["bias"] == "NEUTRAL":
                sesgo["bias"] = "BULLISH"
                sesgo["razones"].append("Patrón alcista en la última vela")
        elif "bearish" in dirs and sesgo["bias"] != "BULLISH":
            if sesgo["bias"] == "NEUTRAL":
                sesgo["bias"] = "BEARISH"
                sesgo["razones"].append("Patrón bajista en la última vela")

    # Últimas 5 velas para el frontend
    ultimas = df.tail(5).copy()
    # Normalizar columna de fecha
    if hasattr(ultimas.index, "strftime"):
        fechas = ultimas.index.strftime("%Y-%m-%d")
    else:
        fechas = [str(x)[:10] for x in ultimas.index]

    velas_json = []
    for i, (_, row) in enumerate(ultimas.iterrows()):
        velas_json.append({
            "date": fechas[i],
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
            "volume": int(row["volume"]),
        })

    return {
        "ticker": ticker,
        "interval": interval,
        "sesgo": sesgo,
        "patrones": patrones,
        "velas_recientes": velas_json,
    }
