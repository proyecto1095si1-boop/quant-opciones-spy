import { useCallback, useEffect, useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import MarketNode from './nodes/MarketNode'
import QuantEngineNode from './nodes/QuantEngineNode'
import SignalNode from './nodes/SignalNode'
import PaperNode from './nodes/PaperNode'
import { useStore } from './store'

const nodeTypes = {
  market: MarketNode,
  quant: QuantEngineNode,
  signal: SignalNode,
  paper: PaperNode,
}

const initialNodes = [
  {
    id: 'market',
    type: 'market',
    position: { x: 40, y: 160 },
    data: {},
  },
  {
    id: 'quant',
    type: 'quant',
    position: { x: 340, y: 120 },
    data: {},
  },
  {
    id: 'signal',
    type: 'signal',
    position: { x: 700, y: 80 },
    data: {},
  },
  {
    id: 'paper',
    type: 'paper',
    position: { x: 700, y: 420 },
    data: {},
  },
]

const initialEdges = [
  {
    id: 'e-market-quant',
    source: 'market',
    target: 'quant',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
  },
  {
    id: 'e-quant-signal',
    source: 'quant',
    target: 'signal',
    animated: true,
    style: { stroke: '#8b5cf6', strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' },
  },
  {
    id: 'e-signal-paper',
    source: 'signal',
    target: 'paper',
    animated: false,
    style: { stroke: '#06b6d4', strokeWidth: 1.5, strokeDasharray: '4 4' },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' },
  },
]

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const { ticker, loading, bias, paper, refreshPaper } = useStore((s) => ({
    ticker: s.ticker,
    loading: s.loading,
    bias: s.senal?.bias || s.analisis?.sesgo?.bias,
    paper: s.paper,
    refreshPaper: s.refreshPaper,
  }))

  useEffect(() => { refreshPaper() }, [refreshPaper])

  const onConnect = useCallback(
    (params) => setEdges((eds) => [...eds, { ...params, animated: true }]),
    [setEdges]
  )

  const biasColor = useMemo(() => {
    if (bias === 'BULLISH') return '#22c55e'
    if (bias === 'BEARISH') return '#ef4444'
    return '#94a3b8'
  }, [bias])

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">◈</span>
          <div>
            <h1>Quant Opciones</h1>
            <p>SPY · Price Action → Options Ticket → Paper</p>
          </div>
        </div>
        <div className="topbar-status">
          <span className={`dot ${loading ? 'loading' : 'idle'}`} />
          <span>{loading ? 'Procesando…' : ticker}</span>
          {bias && (
            <span className="bias-chip" style={{ color: biasColor, borderColor: biasColor }}>
              {bias}
            </span>
          )}
          {paper && (
            <span className="bias-chip" style={{ color: '#06b6d4', borderColor: '#06b6d4' }}>
              Paper ${paper.cash?.toLocaleString()} · PnL {paper.realized_pnl >= 0 ? '+' : ''}{paper.realized_pnl}
            </span>
          )}
        </div>
      </header>

      <div className="canvas-wrap">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.4}
          maxZoom={1.5}
          proOptions={{ hideAttribution: true }}
        >
          <Background gap={24} size={1} color="#1e293b" />
          <Controls showInteractive={false} />
          <MiniMap
            nodeColor={(n) => {
              if (n.type === 'market') return '#3b82f6'
              if (n.type === 'quant') return '#8b5cf6'
              if (n.type === 'paper') return '#0ea5e9'
              return '#06b6d4'
            }}
            maskColor="rgba(15,23,42,0.8)"
          />
        </ReactFlow>
      </div>

      <footer className="footer">
        <span>Proyecto educativo · No es asesoría financiera</span>
        <span>Backend → localhost:8000 · Frontend → React Flow</span>
      </footer>
    </div>
  )
}
