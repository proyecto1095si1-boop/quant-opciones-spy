import { Handle, Position } from '@xyflow/react'
import { useEffect, useState } from 'react'
import { useStore } from '../store'
import { api } from '../api'

export default function PaperNode() {
  const { paper, refreshPaper, paperLoading } = useStore()
  const [positions, setPositions] = useState([])
  const [historial, setHistorial] = useState([])
  const [closeId, setCloseId] = useState(null)
  const [closePrem, setClosePrem] = useState('')
  const [msg, setMsg] = useState(null)

  const load = async () => {
    try {
      const [pos, hist] = await Promise.all([
        api.paperPosiciones(),
        api.paperHistorial(10),
      ])
      setPositions(pos.positions || [])
      setHistorial(hist.closed || [])
      await refreshPaper()
    } catch (e) {
      setMsg(e.message)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleClose = async () => {
    if (!closeId || closePrem === '') return
    try {
      await api.paperCerrar(closeId, Number(closePrem))
      setCloseId(null)
      setClosePrem('')
      setMsg('Posición cerrada')
      await load()
    } catch (e) {
      setMsg(e.message)
    }
  }

  const handleReset = async () => {
    if (!confirm('?¿Reiniciar account paper a $100,000? Se borra el historial.')) return
    try {
      await api.paperReset(100000)
      setMsg('Account reiniciado')
      await load()
    } catch (e) {
      setMsg(e.message)
    }
  }

  return (
    <div className="node paper-node">
      <Handle type="target" position={Position.Left} id="in" />
      <div className="node-header">
        <span className="node-icon">📒</span>
        <span className="node-title">Paper Journal</span>
      </div>
      <div className="node-body">
        {paper && (
          <div className="paper-stats">
            <div>
              <span className="label">Cash</span>
              <span className="value">${paper.cash?.toLocaleString()}</span>
            </div>
            <div>
              <span className="label">PnL</span>
              <span className={`value ${paper.realized_pnl >= 0 ? 'bull' : 'bear'}`}>
                {paper.realized_pnl >= 0 ? '+' : ''}
                {paper.realized_pnl}
              </span>
            </div>
            <div>
              <span className="label">Open</span>
              <span className="value">{paper.posiciones_abiertas}</span>
            </div>
            <div>
              <span className="label">Winrate</span>
              <span className="value">
                {paper.winrate != null ? `${paper.winrate}%` : '—'}
              </span>
            </div>
          </div>
        )}

        {positions.length > 0 && (
          <div className="paper-section">
            <span className="label">Abiertas</span>
            {positions.map((p) => (
              <div key={p.id} className="paper-row">
                <div className="paper-row-main">
                  <span className="mono">{p.symbol || p.strike}</span>
                  <span className="muted">
                    {p.tipo?.toUpperCase()} ×{p.qty} @ ${p.premium}
                  </span>
                </div>
                <button
                  className="btn-tiny"
                  onClick={() => {
                    setCloseId(p.id)
                    setClosePrem(String(p.premium))
                  }}
                >
                  Cerrar
                </button>
              </div>
            ))}
          </div>
        )}

        {closeId && (
          <div className="close-box">
            <span className="label">Prima salida — {closeId}</span>
            <div className="close-row">
              <input
                type="number"
                step="0.05"
                value={closePrem}
                onChange={(e) => setClosePrem(e.target.value)}
              />
              <button className="btn-tiny primary" onClick={handleClose}>
                OK
              </button>
              <button className="btn-tiny" onClick={() => setCloseId(null)}>
                ×
              </button>
            </div>
          </div>
        )}

        {historial.length > 0 && (
          <div className="paper-section">
            <span className="label">Últimos cerrados</span>
            {historial.slice(0, 5).map((t) => (
              <div key={t.id + t.closed_at} className="paper-row hist">
                <span className="mono">{t.strike} {t.tipo}</span>
                <span className={t.pnl >= 0 ? 'bull' : 'bear'}>
                  {t.pnl >= 0 ? '+' : ''}
                  {t.pnl}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="paper-actions">
          <button className="btn-tiny" onClick={load} disabled={paperLoading}>
            Refresh
          </button>
          <button className="btn-tiny danger" onClick={handleReset}>
            Reset
          </button>
        </div>

        {msg && <div className="node-meta">{msg}</div>}
      </div>
    </div>
  )
}
