'use client'

import { useCallback, useEffect } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  type Node,
  type Edge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import {
  AgentNode,
  ToolNode,
  ApprovalNode,
  PolicyNode,
  ConditionNode,
  TriggerNode,
} from './nodes'
import { useWebSocket } from '@/lib/hooks/use-websocket'
import { useWorkflowStore } from '@/lib/stores/workflow-store'
import { ApprovalDialog } from './approval-dialog'
import type { MeshNodeData, WorkflowNode, WorkflowEdge, NodeStatus } from '@/lib/types'

// ─── Node Types Registry ────────────────────────────────────

const nodeTypes = {
  agent: AgentNode,
  tool: ToolNode,
  approval: ApprovalNode,
  policy: PolicyNode,
  condition: ConditionNode,
  trigger: TriggerNode,
}

// ─── Convert persisted nodes → React Flow nodes ──────────────

function toRFNode(n: WorkflowNode): Node {
  return {
    id: n.id,
    type: n.nodeType,
    position: { x: n.positionX, y: n.positionY },
    data: {
      label: n.label,
      status: n.status,
      nodeType: n.nodeType,
      config: n.config,
      description: n.config?.description as string | undefined,
    } satisfies MeshNodeData,
  }
}

function toReactFlowNodes(workflowNodes: WorkflowNode[]): Node[] {
  return workflowNodes.map(toRFNode)
}

// ─── Convert persisted edges → React Flow edges ─────────────

function toReactFlowEdges(workflowEdges: WorkflowEdge[]): Edge[] {
  return workflowEdges.map((e) => ({
    id: e.id,
    source: e.sourceNodeId,
    target: e.targetNodeId,
    sourceHandle: e.sourceHandle || undefined,
    targetHandle: e.targetHandle || undefined,
    type: e.edgeType || 'smoothstep',
    label: e.label,
    animated: e.animated,
    style: { stroke: '#475569', strokeWidth: 2 },
  }))
}

// ─── Canvas Component ───────────────────────────────────────

interface WorkflowCanvasProps {
  workflowId: string
}

export function WorkflowCanvas({ workflowId }: WorkflowCanvasProps) {
  const nodes = useWorkflowStore((s) => s.nodes)
  const edges = useWorkflowStore((s) => s.edges)
  const addNodeToStore = useWorkflowStore((s) => s.addNode)
  const addEdgeToStore = useWorkflowStore((s) => s.addEdge)

  const [rfNodes, setRfNodes, onNodesChange] = useNodesState<Node>([])
  const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState<Edge>([])

  const { liveNodeStatus, liveNodeMetrics, approvalRequest, sendApproval } = useWebSocket(workflowId)

  // Expose setRfNodes to the Zustand store so the toolbar can add nodes directly
  useEffect(() => {
    useWorkflowStore.setState({ _setRfNodes: setRfNodes })
    return () => { useWorkflowStore.setState({ _setRfNodes: undefined }) }
  }, [setRfNodes])

  // Initialize React Flow state from store
  useEffect(() => {
    setRfNodes(toReactFlowNodes(nodes))
    setRfEdges(toReactFlowEdges(edges))
  }, [nodes, edges, setRfNodes, setRfEdges])

  // Sync live WebSocket status updates to React Flow nodes
  useEffect(() => {
    if (Object.keys(liveNodeStatus).length === 0) return

    setRfNodes((nds) =>
      nds.map((n) => {
        const status = liveNodeStatus[n.id]
        const metrics = liveNodeMetrics[n.id]
        if (!status && !metrics) return n
        return {
          ...n,
          data: { ...n.data, ...(status ? { status } : {}), ...(metrics ? { metrics } : {}), },
        }
      }),
    )

    setRfEdges((eds) =>
      eds.map((e) => {
        const sourceStatus = liveNodeStatus[e.source]
        const isRunning = sourceStatus === 'running'
        const isSuccess = sourceStatus === 'success'
        const hasActivity = isRunning || isSuccess
        return {
          ...e,
          animated: hasActivity || e.animated,
          style: {
            ...e.style,
            stroke: isRunning ? '#34d399' : isSuccess ? '#10b981' : '#475569',
            strokeWidth: hasActivity ? 3 : 2,
          },
        }
      }),
    )
  }, [liveNodeStatus, liveNodeMetrics, setRfNodes, setRfEdges])

  // Handle new connections
  const onConnect = useCallback(
    (connection: Connection) => {
      const newEdge: WorkflowEdge = {
        id: `edge-${Date.now()}`,
        workflowId,
        sourceNodeId: connection.source,
        targetNodeId: connection.target,
        sourceHandle: connection.sourceHandle || undefined,
        targetHandle: connection.targetHandle || undefined,
        edgeType: 'smoothstep',
        animated: true,
      }
      addEdgeToStore(newEdge)
      setRfEdges((eds) =>
        addEdge({ ...connection, type: 'smoothstep', animated: true, style: { stroke: '#475569', strokeWidth: 2 } }, eds),
      )
    },
    [workflowId, addEdgeToStore, setRfEdges],
  )

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        className="bg-mission-950"
        proOptions={{ hideAttribution: true }}
        fitView
        snapToGrid
        snapGrid={[16, 16]}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: false,
          style: { stroke: '#475569', strokeWidth: 2 },
        }}>
        <Background color="#1e293b" gap={24} size={1} />
        <Controls className="!bg-mission-900 !border !border-mission-800 !rounded-lg" position="bottom-left" />
        <MiniMap
          style={{ backgroundColor: 'rgb(15 23 42 / 0.9)' }}
          nodeColor={(n) => {
            const status = (n.data as MeshNodeData)?.status
            if (status === 'running') return '#34d399'
            if (status === 'failed') return '#ef4444'
            if (status === 'success') return '#10b981'
            return '#475569'
          }}
          maskColor="rgba(15, 23, 42, 0.7)"
          className="!rounded-lg !border !border-mission-800"
        />
      </ReactFlow>

      {approvalRequest && (
        <ApprovalDialog
          data={approvalRequest as unknown as {
            executionId: string; approvalId: string; nodeId: string;
            nodeLabel: string; reason: string; context?: Record<string, unknown>;
          }}
          onApprove={(approvalId) => sendApproval(approvalId, "approved")}
          onReject={(approvalId) => sendApproval(approvalId, "rejected", "Rejected by operator")}
        />
      )}
    </div>
  )
}
