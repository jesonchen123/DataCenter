import { useState, useEffect } from 'react'
import type { ProcessTask, TaskLog, TimelineStep, SuccessRates } from '@/types/processTask'
import {
  X,
  RefreshCw,
  Download,
  CheckCircle,
  Loader,
  Upload,
  AlertTriangle,
  Send,
} from 'lucide-react'

/* ── derive timeline from current_step ──────────── */
function deriveTimeline(task: ProcessTask): TimelineStep[] {
  const steps: TimelineStep[] = [
    { label: '文档上传', status: 'pending', time: null, description: null },
    { label: '文档解析', status: 'pending', time: null, description: null },
    { label: '内容验证', status: 'pending', time: null, description: null },
    { label: '审核提交', status: 'pending', time: null, description: null },
  ]

  const stepOrder = ['parse', 'validate', 'review']
  const currentIdx = stepOrder.indexOf(task.current_step || '')

  // Still queued — nothing has started
  if (task.status === 'pending' && task.current_step === 'queued') {
    return steps
  }

  // Upload is always done once we're past "queued"
  steps[0].status = 'completed'
  steps[0].time = task.created_at
  steps[0].description = '上传成功'

  // Fully complete
  const isDone = task.status === 'completed' || task.status === 'success'
  if (isDone && task.current_step === 'completed') {
    for (let i = 1; i < steps.length; i++) {
      steps[i].status = 'completed'
    }
    steps[3].description = '已同步到审核中心'
    return steps
  }

  // Failed
  if (task.status === 'failed') {
    for (let i = 1; i < steps.length; i++) {
      const stepI = i - 1
      if (stepI < currentIdx) {
        steps[i].status = 'completed'
      } else if (stepI === currentIdx || currentIdx < 0) {
        steps[i].status = 'active'
        steps[i].label = steps[i].label + ' (失败)'
        steps[i].description = task.error_message || '处理失败'
      }
    }
    return steps
  }

  // Running or waiting at review step
  for (let i = 0; i < stepOrder.length; i++) {
    const timelineIdx = i + 1
    if (currentIdx > i) {
      steps[timelineIdx].status = 'completed'
    } else if (currentIdx === i) {
      steps[timelineIdx].status = 'active'
      steps[timelineIdx].description =
        task.current_step === 'review'
          ? '等待人工提交'
          : `当前步骤 · ${task.progress}%`
    }
  }

  return steps
}

function deriveSuccessRates(task: ProcessTask): SuccessRates {
  const sr = (task.step_result as Record<string, unknown>) || {}
  return {
    parse: typeof sr.parse_rate === 'number' ? sr.parse_rate as number : null,
    validate: typeof sr.validate_rate === 'number' ? sr.validate_rate as number : null,
    review: typeof sr.review_rate === 'number' ? sr.review_rate as number : null,
  }
}

/* ── helpers ────────────────────────────────────── */
const LOG_ICON: Record<string, typeof CheckCircle> = {
  success: CheckCircle,
  completed: CheckCircle,
  running: Loader,
  pending: Loader,
  failed: X,
  error: X,
}
const LOG_COLOR: Record<string, string> = {
  success: '#52c41a',
  completed: '#52c41a',
  running: '#0066CC',
  pending: '#0066CC',
  failed: '#cf1322',
  error: '#cf1322',
}

function formatLogTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch { return iso }
}

/* ── component ──────────────────────────────────── */
interface TaskDetailProps {
  detail: ProcessTask | null
  loading: boolean
  logs: TaskLog[]
  logsLoading: boolean
  open: boolean
  onClose: () => void
  onSubmitToReview: () => Promise<void>
}

export function TaskDetail({
  detail,
  loading,
  logs,
  logsLoading,
  open,
  onClose,
  onSubmitToReview,
}: TaskDetailProps) {
  const [syncing, setSyncing] = useState(false)
  const [syncError, setSyncError] = useState<string | null>(null)
  const [syncSuccess, setSyncSuccess] = useState(false)

  // Reset submit states when task changes
  useEffect(() => {
    setSyncError(null)
    setSyncSuccess(false)
  }, [detail?.id])

  const handleSubmitToReview = async () => {
    setSyncing(true)
    setSyncError(null)
    setSyncSuccess(false)
    try {
      await onSubmitToReview()
      setSyncSuccess(true)
    } catch (err: unknown) {
      setSyncError(err instanceof Error ? err.message : '提交失败，请重试')
    } finally {
      setSyncing(false)
    }
  }

  if (!open) return null

  return (
    <aside
      className="flex-shrink-0 overflow-y-auto bg-white border-l border-gray-200"
      style={{
        width: 360,
        boxShadow: '-4px 0 16px rgba(0,0,0,0.04)',
        animation: 'slideInRight 0.3s ease',
      }}
    >
      {/* sticky header */}
      <div className="sticky top-0 bg-white border-b border-gray-100 px-5 py-4 flex items-center justify-between z-10">
        <h3 className="font-semibold" style={{ fontSize: 15, color: '#1a1a2e' }}>
          任务详情
        </h3>
        <button
          onClick={onClose}
          className="p-1.5 rounded-md hover:bg-gray-100 transition cursor-pointer border-0 bg-transparent"
        >
          <X size={18} color="#999" />
        </button>
      </div>

      <div className="px-5 py-4">
        {loading ? (
          <div className="space-y-3 animate-pulse">
            <div className="h-4 w-32 bg-gray-100 rounded" />
            <div className="h-24 bg-gray-50 rounded-lg" />
            <div className="h-4 w-48 bg-gray-100 rounded" />
            <div className="h-32 bg-gray-50 rounded-lg" />
          </div>
        ) : detail ? (
          <>
            {/* ── Basic Info ──────────────────────── */}
            <div className="mb-5">
              <h4 className="font-medium mb-3" style={{ fontSize: 13, color: '#1a1a2e' }}>
                基本信息
              </h4>
              <div className="space-y-2.5">
                <InfoRow label="任务 ID" value={`#${detail.task_no.slice(-5)}`} color="#0066CC" />
                <InfoRow label="文档名称" value={detail.doc_name} bold />
                <InfoRow label="创建时间" value={formatLogTime(detail.created_at)} />
                <InfoRow label="指派人" value={detail.assignee_name} />
                <InfoRow label="文档类型" value={detail.doc_category} />
              </div>
            </div>

            <hr className="border-gray-100 my-4" />

            {/* ── Progress Timeline ──────────────── */}
            <div className="mb-5">
              <h4 className="font-medium mb-3" style={{ fontSize: 13, color: '#1a1a2e' }}>
                处理进度
              </h4>
              <div className="space-y-0">
                {deriveTimeline(detail).map((step, i, arr) => {
                  const isLast = i === arr.length - 1
                  const dotClass =
                    step.status === 'completed'
                      ? 'timeline-dot completed'
                      : step.status === 'active'
                        ? 'timeline-dot active'
                        : 'timeline-dot pending'

                  const lineColor =
                    step.status === 'completed' ? '#52c41a' : '#d9d9d9'

                  const textColor =
                    step.status === 'completed'
                      ? '#333'
                      : step.status === 'active'
                        ? '#0066CC'
                        : '#bbb'

                  const badgeStyle =
                    step.status === 'completed'
                      ? { background: '#f6ffed', color: '#389e0d', border: '1px solid #b7eb8f' }
                      : step.status === 'active'
                        ? { background: '#e6f7ff', color: '#0066CC', border: '1px solid #91d5ff' }
                        : { background: '#fafafa', color: '#bbb', border: '1px solid #e8e8e8' }

                  const badgeText =
                    step.status === 'completed' ? '完成' : step.status === 'active' ? '进行中' : '待处理'

                  return (
                    <div key={i} className="flex gap-3" style={{ minHeight: isLast ? 36 : 40 }}>
                      <div className="flex flex-col items-center">
                        <div className={dotClass} />
                        {!isLast && (
                          <div style={{ width: 2, height: '100%', background: lineColor }} />
                        )}
                      </div>
                      <div className={isLast ? '' : 'pb-3'}>
                        <p style={{ fontSize: 13, fontWeight: 500, color: textColor }}>
                          {step.label}
                        </p>
                        {step.description && (
                          <p style={{ fontSize: 11, color: '#999' }}>{step.description}</p>
                        )}
                        {step.time && (
                          <p style={{ fontSize: 11, color: '#999' }}>{formatLogTime(step.time)}</p>
                        )}
                      </div>
                      <span
                        className="ml-auto status-badge"
                        style={{ ...badgeStyle, height: 'fit-content' }}
                      >
                        {badgeText}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>

            <hr className="border-gray-100 my-4" />

            {/* ── Success Rates ──────────────────── */}
            {(() => {
              const rates = deriveSuccessRates(detail)
              const hasAny = rates.parse !== null || rates.validate !== null || rates.review !== null
              if (!hasAny) return null
              return (
                <div className="mb-5">
                  <h4 className="font-medium mb-3" style={{ fontSize: 13, color: '#1a1a2e' }}>
                    成功率明细
                  </h4>
                  <div className="space-y-3">
                    {rates.parse !== null && (
                      <RateBar label="解析成功率" pct={rates.parse} />
                    )}
                    {rates.validate !== null && (
                      <RateBar label="验证成功率" pct={rates.validate} />
                    )}
                    {rates.review !== null && (
                      <RateBar label="审核成功率" pct={rates.review} />
                    )}
                    {rates.parse === null && rates.validate === null && rates.review === null && (
                      <p style={{ fontSize: 12, color: '#999' }}>暂无明细数据</p>
                    )}
                  </div>
                </div>
              )
            })()}

            <hr className="border-gray-100 my-4" />

            {/* ── LLM Logs ──────────────────────── */}
            <div className="mb-5">
              <h4 className="font-medium mb-3" style={{ fontSize: 13, color: '#1a1a2e' }}>
                LLM 处理日志
              </h4>
              <div className="max-h-48 overflow-y-auto">
                {logsLoading ? (
                  <div className="space-y-2 animate-pulse">
                    <div className="h-10 bg-gray-50 rounded" />
                    <div className="h-10 bg-gray-50 rounded" />
                    <div className="h-10 bg-gray-50 rounded" />
                  </div>
                ) : logs.length === 0 ? (
                  <p style={{ fontSize: 12, color: '#999' }}>暂无日志</p>
                ) : (
                  logs.map((log) => {
                    const Icon = LOG_ICON[log.status] || Loader
                    const iconColor = LOG_COLOR[log.status] || '#888'
                    const label =
                      log.parsed_output && (log.parsed_output as Record<string, unknown>).message
                        ? String((log.parsed_output as Record<string, unknown>).message)
                        : log.status === 'success' || log.status === 'completed'
                          ? '处理完成'
                          : log.status === 'failed'
                            ? log.error_message || '处理失败'
                            : '处理中...'

                    return (
                      <div key={log.id} className="log-entry">
                        <div className="flex items-start gap-2">
                          <Icon size={14} color={iconColor} style={{ marginTop: 1, flexShrink: 0 }} />
                          <div className="flex-1 min-w-0">
                            <p style={{ fontSize: 12, color: '#333' }}>{label}</p>
                            <p style={{ fontSize: 11, color: '#bbb' }}>
                              {formatLogTime(log.created_at)}
                            </p>
                          </div>
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </div>

            {/* ── Actions ────────────────────────── */}
            <div className="pt-2 border-t border-gray-100">
              {/* Error message */}
              {syncError && (
                <div
                  className="flex items-center gap-1.5 mb-2 px-3 py-2 rounded-md"
                  style={{ background: '#fff1f0', border: '1px solid #ffa39e', fontSize: 12, color: '#cf1322' }}
                >
                  <AlertTriangle size={14} />
                  {syncError}
                </div>
              )}
              {/* Success message */}
              {syncSuccess && (
                <div
                  className="flex items-center gap-1.5 mb-2 px-3 py-2 rounded-md"
                  style={{ background: '#f6ffed', border: '1px solid #b7eb8f', fontSize: 12, color: '#389e0d' }}
                >
                  <CheckCircle size={14} />
                  已成功提交到审核中心
                </div>
              )}
              <div className="flex gap-3">
                {/* Show "审核提交" button when waiting at review step */}
                {detail.current_step === 'review' && (detail.status === 'success' || detail.status === 'completed') ? (
                  <button
                    className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-white font-medium transition cursor-pointer border-0 hover:shadow-md disabled:opacity-60 disabled:cursor-not-allowed"
                    style={{ background: '#389e0d', fontSize: 13 }}
                    disabled={syncing || syncSuccess}
                    onClick={handleSubmitToReview}
                  >
                    <Send size={14} />
                    {syncing ? '提交中...' : syncSuccess ? '已提交' : '审核提交'}
                  </button>
                ) : (
                  <>
                    <button
                      className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-white font-medium transition cursor-pointer border-0 hover:shadow-md"
                      style={{ background: '#0066CC', fontSize: 13 }}
                    >
                      <RefreshCw size={14} />
                      重试
                    </button>
                    <button
                      className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg border border-gray-200 font-medium transition cursor-pointer hover:bg-gray-50 bg-white"
                      style={{ fontSize: 13, color: '#555' }}
                    >
                      <Download size={14} />
                      导出日志
                    </button>
                  </>
                )}
              </div>
            </div>
          </>
        ) : (
          <p className="text-[13px] text-gray-400 py-8 text-center">
            点击任务行查看详情
          </p>
        )}
      </div>
    </aside>
  )
}

/* ── sub-components ──────────────────────────────── */

function InfoRow({
  label,
  value,
  bold,
  color,
}: {
  label: string
  value: string
  bold?: boolean
  color?: string
}) {
  return (
    <div className="flex justify-between">
      <span style={{ fontSize: 12, color: '#888' }}>{label}</span>
      <span style={{ fontSize: 12, color: color || '#333', fontWeight: bold ? 500 : 400 }}>
        {value}
      </span>
    </div>
  )
}

function RateBar({ label, pct }: { label: string; pct: number }) {
  const color = pct >= 90 ? '#52c41a' : pct >= 60 ? '#faad14' : '#ff4d4f'
  return (
    <div>
      <div className="flex justify-between mb-1.5">
        <span style={{ fontSize: 12, color: '#666' }}>{label}</span>
        <span style={{ fontSize: 12, color, fontWeight: 600 }}>{pct}%</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  )
}
