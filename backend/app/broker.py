"""
Adaptador de broker: Alpaca Paper Trading.

Si hay ALPACA_API_KEY + ALPACA_SECRET_KEY en el entorno (o .env),
puede consultar cuenta y enviar órdenes de opciones en paper.

Si no hay keys, el sistema sigue usando solo el journal local (`paper.py`).
"""

from __future__ import annotations

import os
from typing import Any, Optional

try:
    from pathlib import Path

    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
except Exception:
    pass

ALPACA_KEY = os.getenv("ALPACA_API_KEY", "").strip()
ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY", "").strip()
ALPACA_BASE = os.getenv(
    "ALPACA_BASE_URL",
    "https://paper-api.alpaca.markets",
).rstrip("/")
ALPACA_DATA = os.getenv(
    "ALPACA_DATA_URL",
    "https://data.alpaca.markets",
).rstrip("/")


def configurado() -> bool:
    return bool(ALPACA_KEY and ALPACA_SECRET)


def _headers() -> dict[str, str]:
    return {
        "APCA-API-KEY-ID": ALPACA_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET,
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, json_body: dict | None = None, base: str | None = None) -> dict[str, Any]:
    import urllib.error
    import urllib.request
    import json as _json

    if not configurado():
        raise RuntimeError(
            "Alpaca no configurado. Definí ALPACA_API_KEY y ALPACA_SECRET_KEY "
            "en .env o variables de entorno (cuenta paper gratuita en alpaca.markets)."
        )

    url = f"{base or ALPACA_BASE}{path}"
    data = _json.dumps(json_body).encode() if json_body is not None else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return _json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else str(e)
        raise RuntimeError(f"Alpaca HTTP {e.code}: {err_body}") from e


def status() -> dict[str, Any]:
    if not configurado():
        return {
            "broker": "alpaca",
            "mode": "paper",
            "configured": False,
            "message": "Sin API keys. Usá solo paper local (/paper/*) o configurá .env",
        }
    try:
        acct = _request("GET", "/v2/account")
        return {
            "broker": "alpaca",
            "mode": "paper" if "paper" in ALPACA_BASE else "live",
            "configured": True,
            "status": acct.get("status"),
            "equity": float(acct.get("equity") or 0),
            "cash": float(acct.get("cash") or 0),
            "buying_power": float(acct.get("buying_power") or 0),
            "currency": acct.get("currency", "USD"),
            "account_number": acct.get("account_number"),
        }
    except Exception as e:
        return {
            "broker": "alpaca",
            "mode": "paper",
            "configured": True,
            "error": str(e),
        }


def account() -> dict[str, Any]:
    return _request("GET", "/v2/account")


def positions() -> list[dict[str, Any]]:
    return _request("GET", "/v2/positions")  # type: ignore[return-value]


def orders(status: str = "open", limit: int = 50) -> list[dict[str, Any]]:
    return _request("GET", f"/v2/orders?status={status}&limit={limit}&direction=desc")  # type: ignore


def place_option_order(
    symbol: str,
    qty: int = 1,
    side: str = "buy",
    order_type: str = "market",
    time_in_force: str = "day",
    limit_price: Optional[float] = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "symbol": symbol,
        "qty": str(qty),
        "side": side,
        "type": order_type,
        "time_in_force": time_in_force,
        "asset_class": "us_option",
    }
    if order_type == "limit" and limit_price is not None:
        body["limit_price"] = str(limit_price)

    return _request("POST", "/v2/orders", json_body=body)


def place_from_signal(senal: dict[str, Any], qty: int = 1) -> dict[str, Any]:
    from app import paper as local_paper

    if senal.get("accion") != "COMPRAR":
        raise ValueError("Señal no es COMPRAR")

    c = senal.get("contrato_recomendado")
    if not c or not c.get("symbol"):
        raise ValueError("Sin contrato recomendado")

    symbol = c["symbol"]
    order = place_option_order(symbol=symbol, qty=qty, side="buy", order_type="market")

    local_result = None
    try:
        local_result = local_paper.abrir_desde_senal(senal, qty=qty, notas=f"alpaca:{order.get('id')}")
    except Exception as e:
        local_result = {"warning": f"Orden Alpaca OK pero journal local falló: {e}"}

    return {
        "ok": True,
        "broker": "alpaca",
        "order": order,
        "local": local_result,
    }
