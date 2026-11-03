"""
Paper trading: journal de operaciones simuladas, posiciones y PnL.

Almacenamiento local en JSON (sin base de datos externa).
Ideal para validar el motor antes de conectar un broker real.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
JOURNAL_PATH = DATA_DIR / "paper_journal.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not JOURNAL_PATH.exists():
        return {"positions": [], "closed": [], "cash": 100_000.0, "updated_at": _now()}
    with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    with open(JOURNAL_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def estado() -> dict[str, Any]:
    data = _load()
    open_pos = data.get("positions", [])
    closed = data.get("closed", [])
    cash = float(data.get("cash", 100_000))
    realized = sum(float(t.get("pnl") or 0) for t in closed)
    capital_en_riesgo = sum(
        float(p.get("premium") or 0) * 100 * int(p.get("qty") or 1)
        for p in open_pos
    )
    wins = [t for t in closed if float(t.get("pnl") or 0) > 0]
    losses = [t for t in closed if float(t.get("pnl") or 0) < 0]
    return {
        "cash": round(cash, 2),
        "capital_en_riesgo": round(capital_en_riesgo, 2),
        "equity_aprox": round(cash + capital_en_riesgo, 2),
        "realized_pnl": round(realized, 2),
        "posiciones_abiertas": len(open_pos),
        "trades_cerrados": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "winrate": round(len(wins) / len(closed) * 100, 1) if closed else None,
        "updated_at": data.get("updated_at"),
    }


def listar_posiciones() -> list[dict]:
    return _load().get("positions", [])


def listar_cerrados(limit: int = 50) -> list[dict]:
    closed = _load().get("closed", [])
    return list(reversed(closed[-limit:]))


def abrir_desde_senal(senal: dict[str, Any], qty: int = 1, notas: str = "") -> dict[str, Any]:
    if senal.get("accion") != "COMPRAR":
        raise ValueError("La señal no es de compra (ESPERAR o sin contrato)")
    c = senal.get("contrato_recomendado")
    if not c:
        raise ValueError("La señal no trae contrato_recomendado")
    premium = float(c.get("mid") or c.get("ask") or c.get("bid") or 0)
    if premium <= 0:
        raise ValueError("Prima inválida en el contrato")
    costo = premium * 100 * qty
    data = _load()
    cash = float(data.get("cash", 100_000))
    if costo > cash:
        raise ValueError(f"Cash insuficiente: necesitas ${costo:.2f}, tienes ${cash:.2f}")
    pos = {
        "id": str(uuid.uuid4())[:8],
        "opened_at": _now(),
        "ticker": senal.get("ticker", "SPY"),
        "bias": senal.get("bias"),
        "tipo": senal.get("tipo_opcion"),
        "symbol": c.get("symbol"),
        "strike": c.get("strike"),
        "vencimiento": senal.get("vencimiento"),
        "dte_entrada": senal.get("dte"),
        "qty": qty,
        "side": "long",
        "premium": premium,
        "costo_total": round(costo, 2),
        "delta_entrada": c.get("delta"),
        "theta_entrada": c.get("theta"),
        "iv_entrada": c.get("iv"),
        "justificacion": senal.get("justificacion"),
        "notas": notas,
        "status": "open",
    }
    data["cash"] = round(cash - costo, 2)
    data.setdefault("positions", []).append(pos)
    _save(data)
    return {"ok": True, "posicion": pos, "cash_restante": data["cash"]}


def abrir_manual(
    ticker: str, tipo: Literal["call", "put"], symbol: str, strike: float,
    premium: float, qty: int = 1, vencimiento: str = "", notas: str = "",
) -> dict[str, Any]:
    if premium <= 0 or qty < 1:
        raise ValueError("premium y qty deben ser positivos")
    costo = premium * 100 * qty
    data = _load()
    cash = float(data.get("cash", 100_000))
    if costo > cash:
        raise ValueError(f"Cash insuficiente: ${costo:.2f} > ${cash:.2f}")
    pos = {
        "id": str(uuid.uuid4())[:8],
        "opened_at": _now(),
        "ticker": ticker.upper(),
        "bias": None,
        "tipo": tipo,
        "symbol": symbol,
        "strike": strike,
        "vencimiento": vencimiento,
        "dte_entrada": None,
        "qty": qty,
        "side": "long",
        "premium": premium,
        "costo_total": round(costo, 2),
        "delta_entrada": None,
        "theta_entrada": None,
        "iv_entrada": None,
        "justificacion": "Entrada manual",
        "notas": notas,
        "status": "open",
    }
    data["cash"] = round(cash - costo, 2)
    data.setdefault("positions", []).append(pos)
    _save(data)
    return {"ok": True, "posicion": pos, "cash_restante": data["cash"]}


def cerrar(position_id: str, premium_salida: float, notas: str = "") -> dict[str, Any]:
    if premium_salida < 0:
        raise ValueError("premium_salida no puede ser negativa")
    data = _load()
    positions = data.get("positions", [])
    idx = next((i for i, p in enumerate(positions) if p["id"] == position_id), None)
    if idx is None:
        raise ValueError(f"Posición {position_id} no encontrada o ya cerrada")
    pos = positions.pop(idx)
    qty = int(pos.get("qty") or 1)
    prem_in = float(pos["premium"])
    pnl = (premium_salida - prem_in) * 100 * qty
    closed = {
        **pos,
        "status": "closed",
        "closed_at": _now(),
        "premium_salida": premium_salida,
        "pnl": round(pnl, 2),
        "notas_cierre": notas,
        "resultado": "win" if pnl > 0 else ("loss" if pnl < 0 else "scratch"),
    }
    data["cash"] = round(float(data.get("cash", 0)) + premium_salida * 100 * qty, 2)
    data.setdefault("closed", []).append(closed)
    data["positions"] = positions
    _save(data)
    return {"ok": True, "trade": closed, "cash_restante": data["cash"]}


def reset_account(cash: float = 100_000.0) -> dict[str, Any]:
    data = {"positions": [], "closed": [], "cash": float(cash), "updated_at": _now()}
    _save(data)
    return estado()
