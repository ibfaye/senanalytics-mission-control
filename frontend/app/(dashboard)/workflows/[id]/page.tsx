'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { WorkflowCanvas } from '@/components/flow/canvas'
import { WorkflowToolbar } from '@/components/flow/toolbar'
import {
  useWorkflow,
  useSaveWorkflowGraph,
  useExecuteWorkflow,
} from '@/lib/hooks/use-workflows'
import { useWorkflowStore } from '@/lib/stores/workflow-store'
import { useWebSocket } from '@/lib/hooks/use-websocket'
import { useToast } from '@/components/ui/use-toast'
import { Loader2, CheckCircle2, AlertTriangle } from 'lucide-react'

export default function WorkflowDetailPage() {
  const params = useParams<{ id: string }>()
  const workflowId = params.id

  const { data: workflow, isLoading } = useWorkflow(workflowId)
  const {
    currentWorkflow,
    nodes,
    edges,
    setCurrentWorkflow,
    setNodes,
    setEdges,
  } = useWorkflowStore()
  const saveMutation = useSaveWorkflowGraph()
  const executeMutation = useExecuteWorkflow()
  const { toast } = useToast()

  // Track execution state
  const [executing, setExecuting] = useState(false)
  const [completedSteps, setCompletedSteps] = useState(0)
  const [totalSteps, setTotalSteps] = useState(0)
  const { liveNodeStatus, lastEvent } = useWebSocket(
    executing ? workflowId : null,
  )

  // Sync loaded workflow to store
  useEffect(() => {
    if (workflow && (!currentWorkflow || currentWorkflow.id !== workflow.id)) {
      setCurrentWorkflow(workflow)
      setNodes(workflow.nodes || [])
      setEdges(workflow.edges || [])
    }
  }, [workflow, setCurrentWorkflow, setNodes, setEdges])

  // Track execution progress from WebSocket events
  useEffect(() => {
    if (!lastEvent) return

    switch (lastEvent.event) {
      case 'workflow.execution.started':
        setExecuting(true)
        setCompletedSteps(0)
        setTotalSteps(
          (workflow?.nodes || []).filter(
            (n) => n.nodeType === 'agent',
          ).length,
        )
        break

      case 'node.completed':
        setCompletedSteps((prev) => prev + 1)
        break

      case 'workflow.execution.completed':
        setExecuting(false)
        toast({
          title: 'Workflow completed',
          description: 'All agents executed successfully',
        })
        break

      case 'workflow.execution.failed':
        setExecuting(false)
        toast({
          title: 'Workflow failed',
          description: (lastEvent.data?.error as string) || 'An error occurred',
          variant: 'destructive',
        })
        break
    }
  }, [lastEvent, workflow, toast])

  const handleSave = () => {
    saveMutation.mutate({ id: workflowId, nodes, edges })
  }

  const handleExecute = () => {
    executeMutation.mutate(workflowId)
  }

  const isBusy = executing || executeMutation.isPending

  return (
    <div className="flex h-full flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-mission-800 bg-mission-900 px-4 py-2">
        <div className="flex items-center gap-3">
          <h1 className="text-sm font-semibold text-mission-200">
            {workflow?.name || 'Loading...'}
          </h1>
          {workflow && (
            <span
              className={`rounded-full px-2 py-0.5 text-[10px] font-medium
                ${
                  workflow.status === 'active'
                    ? 'bg-emerald-950 text-emerald-400'
                    : 'bg-mission-800 text-mission-400'
                }`}>
              {workflow.status}
            </span>
          )}
        </div>
        <WorkflowToolbar
          workflowId={workflowId}
          onSave={handleSave}
          onExecute={handleExecute}
          isExecuting={isBusy}
        />
      </div>

      {/* Execution Progress Bar */}
      {executing && (
        <div className="flex items-center gap-3 border-b border-mission-800 bg-mission-900/50 px-4 py-1.5">
          <Loader2 className="h-3.5 w-3.5 text-agent-emerald animate-spin" />
          <span className="text-xs text-mission-300">
            Executing {completedSteps}/{totalSteps || '?'} agents
          </span>
          <div className="ml-auto flex items-center gap-2">
            {Object.entries(liveNodeStatus).map(([id, status]) => (
              <span
                key={id}
                className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px]
                  ${
                    status === 'running'
                      ? 'bg-emerald-950 text-emerald-400'
                      : status === 'success'
                        ? 'bg-emerald-950/50 text-emerald-500'
                        : status === 'failed'
                          ? 'bg-red-950 text-red-400'
                          : 'bg-mission-800 text-mission-500'
                  }`}>
                {status === 'running' && (
                  <Loader2 className="h-2.5 w-2.5 animate-spin" />
                )}
                {status === 'success' && (
                  <CheckCircle2 className="h-2.5 w-2.5" />
                )}
                {status === 'failed' && (
                  <AlertTriangle className="h-2.5 w-2.5" />
                )}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Canvas */}
      <div className="flex-1">
        {isLoading ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-mission-500">Loading workflow...</p>
          </div>
        ) : (
          <WorkflowCanvas workflowId={workflowId} />
        )}
      </div>
    </div>
  )
}
