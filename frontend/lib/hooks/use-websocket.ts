'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import type { WSExecutionUpdate, NodeStatus, NodeMetrics } from '@/lib/types'

interface UseWebSocketReturn {
  connected: boolean
  liveNodeStatus: Record<string, NodeStatus>
  liveNodeMetrics: Record<string, NodeMetrics>
  approvalRequest: WSExecutionUpdate['data'] | null
  lastEvent: WSExecutionUpdate | null
  sendApproval: (approvalId: string, decision: string, reason?: string) => void
}

export function useWebSocket(workflowId: string | null): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [liveNodeStatus, setLiveNodeStatus] = useState<
    Record<string, NodeStatus>
  >({})
  const [liveNodeMetrics, setLiveNodeMetrics] = useState<
    Record<string, NodeMetrics>
  >({})
  const [approvalRequest, setApprovalRequest] = useState<
    WSExecutionUpdate['data'] | null
  >(null)
  const [lastEvent, setLastEvent] = useState<WSExecutionUpdate | null>(null)

  useEffect(() => {
    if (!workflowId) return

    const ws = new WebSocket(`ws://localhost:8000/ws/workflows/${workflowId}`)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onerror = () => setConnected(false)

    ws.onmessage = (event) => {
      try {
        const msg: WSExecutionUpdate = JSON.parse(event.data)
        setLastEvent(msg)

        switch (msg.event) {
          case 'node.started':
            setLiveNodeStatus((prev) => ({
              ...prev,
              [msg.data.nodeId]: 'running',
            }))
            break

          case 'node.completed':
            setLiveNodeStatus((prev) => ({
              ...prev,
              [msg.data.nodeId]: 'success',
            }))
            if (msg.data.metrics) {
              setLiveNodeMetrics((prev) => ({
                ...prev,
                [msg.data.nodeId]: msg.data.metrics!,
              }))
            }
            break

          case 'node.failed':
            setLiveNodeStatus((prev) => ({
              ...prev,
              [msg.data.nodeId]: 'failed',
            }))
            break

          case 'approval.requested':
            setApprovalRequest(msg.data)
            break

          case 'workflow.execution.completed':
          case 'workflow.execution.failed':
            setApprovalRequest(null)
            break
        }
      } catch {
        // ignore parse errors
      }
    }

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [workflowId])

  const sendApproval = useCallback(
    (approvalId: string, decision: string, reason?: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            action: 'approval.respond',
            data: { approvalId, decision, reason },
          }),
        )
        setApprovalRequest(null)
      }
    },
    [],
  )

  return {
    connected,
    liveNodeStatus,
    liveNodeMetrics,
    approvalRequest,
    lastEvent,
    sendApproval,
  }
}
