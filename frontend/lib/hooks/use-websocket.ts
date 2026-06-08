"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { WSExecutionUpdate, NodeStatus, NodeMetrics } from "@/lib/types";

interface UseWebSocketReturn {
  connected: boolean;
  liveNodeStatus: Record<string, NodeStatus>;
  liveNodeMetrics: Record<string, NodeMetrics>;
  approvalRequest: WSExecutionUpdate["data"] | null;
  lastEvent: WSExecutionUpdate | null;
  sendApproval: (approvalId: string, decision: string, reason?: string) => void;
}

const MAX_RECONNECT_DELAY = 30_000; // 30 seconds max
const INITIAL_RECONNECT_DELAY = 1_000; // 1 second start
const BACKOFF_MULTIPLIER = 2;

export function useWebSocket(workflowId: string | null): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptRef = useRef(0);
  const mountedRef = useRef(true);

  const [connected, setConnected] = useState(false);
  const [liveNodeStatus, setLiveNodeStatus] = useState<Record<string, NodeStatus>>({});
  const [liveNodeMetrics, setLiveNodeMetrics] = useState<Record<string, NodeMetrics>>({});
  const [approvalRequest, setApprovalRequest] = useState<WSExecutionUpdate["data"] | null>(null);
  const [lastEvent, setLastEvent] = useState<WSExecutionUpdate | null>(null);

  const connect = useCallback(() => {
    if (!workflowId || !mountedRef.current) return;

    // Clear any pending reconnect
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    const port = process.env.BACKEND_PORT || 8000;

    const ws = new WebSocket(`ws://localhost:${port}/ws/workflows/${workflowId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      setConnected(true);
      reconnectAttemptRef.current = 0; // reset on successful connection
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      setConnected(false);

      // Exponential backoff reconnect
      const attempt = reconnectAttemptRef.current;
      const delay = Math.min(
        INITIAL_RECONNECT_DELAY * Math.pow(BACKOFF_MULTIPLIER, attempt),
        MAX_RECONNECT_DELAY
      );
      reconnectAttemptRef.current = attempt + 1;

      console.log(
        `[WS] Disconnected. Reconnecting in ${delay / 1000}s (attempt ${attempt + 1})`
      );

      reconnectTimeoutRef.current = setTimeout(() => {
        if (mountedRef.current) connect();
      }, delay);
    };

    ws.onerror = () => {
      // onclose will fire after this, triggering reconnect
    };

    ws.onmessage = (event) => {
      try {
        const msg: WSExecutionUpdate = JSON.parse(event.data);
        if (!mountedRef.current) return;
        setLastEvent(msg);

        switch (msg.event) {
          case "node.started":
            setLiveNodeStatus((prev) => ({
              ...prev,
              [msg.data.nodeId]: "running",
            }));
            break;

          case "node.completed":
            setLiveNodeStatus((prev) => ({
              ...prev,
              [msg.data.nodeId]: "success",
            }));
            if (msg.data.metrics) {
              setLiveNodeMetrics((prev) => ({
                ...prev,
                [msg.data.nodeId]: msg.data.metrics!,
              }));
            }
            break;

          case "node.failed":
            setLiveNodeStatus((prev) => ({
              ...prev,
              [msg.data.nodeId]: "failed",
            }));
            break;

          case "approval.requested":
            setApprovalRequest(msg.data);
            break;

          case "workflow.execution.completed":
          case "workflow.execution.failed":
            setApprovalRequest(null);
            break;
        }
      } catch {
        // ignore parse errors
      }
    };
  }, [workflowId]);

  // Connect on mount / workflowId change, cleanup on unmount
  useEffect(() => {
    mountedRef.current = true;
    reconnectAttemptRef.current = 0;
    connect();

    return () => {
      mountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  const sendApproval = useCallback(
    (approvalId: string, decision: string, reason?: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            action: "approval.respond",
            data: { approvalId, decision, reason },
          })
        );
        setApprovalRequest(null);
      }
    },
    []
  );

  return {
    connected,
    liveNodeStatus,
    liveNodeMetrics,
    approvalRequest,
    lastEvent,
    sendApproval,
  };
}
