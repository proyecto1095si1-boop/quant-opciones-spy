import { Handle, Position } from '@xyflow/react'
import { useStore } from '../store'

export default function MarketNode({ data }) {
  const { ticker, timeframe, setTicker, setTimeframe, loading } = useStore()

  return (
    <div className="node market-node">
      <div className="node-header">
        <span className="node-icon">📡</span>
        <span className="node-title">Market</span>
      </div>
      <div className="node-body">
        <label>
          Ticker
          <input
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            disabled={loading}
            maxLength={8}
          />
        </label>
        <label>
          Temporalidad
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            disabled={loading}
          >
            <option value="1d">Diaria</option>
            <option value="1h">Horaria</option>
            <option value="4h">4 Horas</option>
          </select>
        </label>
        <div className="node-meta">{ticker} · {timeframe}</div>
      </div>
      <Handle type="source" position={Position.Right} id="out" />
    </div>
  )
}
