import { Handle, Position } from '@xyflow/react'
import { useStore } from '../store'

export default function SignalNode() {
  const { senal, loading } = useStore()

  if (!senal) {
    return (
      <div className="node signal-node empty">
        <Handle type="target" position={Position.Left} id="in" />
        <div className="node-header">
          <span className="node-icon">🎫</span>
          <span className="node-title">Signal</span>
        </div>
        <div className="node-body">
          <p className="placeholder">
            {loading ? 'Esperando resultado…' : 'Ejecutá el motor para ver el ticket'}
          </p>
        </div>
      </div>
    )
  }

  const c = senal.contrato_recomendado
  const isWait = senal.accion === 'ESPERAR'

  return (
    <div className={`node signal-node ${isWait ? 'wait' : 'action'}`}>
      <Handle type="target" position={Position.Left} id="in" />
      <div className="node-header">
        <span className="node-icon">🎫</span>
        <span className="node-title">Signal</span>
        <span className={`accion-pill ${isWait ? 'wait' : 'buy'}`}>
          {senal.accion}
        </span>
      </div>
      <div className="node-body">
        <div className="justificacion">{senal.justificacion}</div>

        {c ? (
          <>
            <div className="contrato">
              <div className="contrato-symbol">{c.symbol}</div>
              <div className="contrato-grid">
                <div>
                  <span className="label">Strike</span>
                  <span className="value">{c.strike}</span>
                </div>
                <div>
                  <span className="label">Mid</span>
                  <span className="value">${c.mid}</span>
                </div>
                <div>
                  <span className="label">Bid / Ask</span>
                  <span className="value">
                    {c.bid} / {c.ask}
                  </span>
                </div>
                <div>
                  <span className="label">Spread</span>
                  <span className="value">{c.spread_pct}%</span>
                </div>
                <div>
                  <span className="label">OI</span>
                  <span className="value">{c.openInterest?.toLocaleString()}</span>
                </div>
                <div>
                  <span className="label">IV</span>
                  <span className="value">
                    {c.iv != null ? `${(c.iv * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
              </div>
            </div>
            {senal.vencimiento && (
              <div className="node-meta">
                Vto {senal.vencimiento} · {senal.dte} DTE · {senal.tipo_opcion?.toUpperCase()}
              </div>
            )}
            {senal.alternativas?.length > 0 && (
              <div className="alternativas">
                <span className="label">Alternativas</span>
                {senal.alternativas.map((a) => (
                  <div key={a.symbol} className="alt-row">
                    {a.strike} · mid ${a.mid} · OI {a.openInterest}
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="sin-contrato">Sin contrato que cumpla filtros</div>
        )}
      </div>
    </div>
  )
}
