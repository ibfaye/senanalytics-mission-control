'use client'

import { useEffect } from 'react'
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
    isExecuting,
  } = useWorkflowStore()
  const saveMutation = useSaveWorkflowGraph()
  const executeMutation = useExecuteWorkflow()

  // Sync loaded workflow to store
  useEffect(() => {
    if (workflow && (!currentWorkflow || currentWorkflow.id !== workflow.id)) {
      setCurrentWorkflow(workflow)
      setNodes(workflow.nodes || [])
      setEdges(workflow.edges || [])
    }
  }, [workflow, setCurrentWorkflow, setNodes, setEdges])

  const handleSave = () => {
    saveMutation.mutate({ id: workflowId, nodes, edges })
  }

  const handleExecute = () => {
    console.log('[Workflow] Execute button clicked for ID:', workflowId)
    executeMutation.mutate(workflowId)
  }

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
          isExecuting={isExecuting || executeMutation.isPending}
        />
      </div>

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
