import { useState } from 'react'
import { Check, Edit3, X, Save, AlertTriangle, AlertCircle, Info, User, Clock, FileText } from 'lucide-react'
import type { ReviewDocument, ReviewAction } from '@/types/review'

const RISK_STYLE: Record<string, { bg: string; color: string; border: string; icon: typeof AlertTriangle; label: string }> = {
  high: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', icon: AlertTriangle, label: '高优先级' },
  medium: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', icon: AlertCircle, label: '中优先级' },
  low: { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', icon: Info, label: '低优先级' },
}

const STATUS_STYLE: Record<string, { bg: string; color: string; border: string; label: string }> = {
  pending_review: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', label: '待审核' },
  need_edit: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', label: '需修改' },
  approved: { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f', label: '已批准' },
  rejected: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', label: '已驳回' },
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toISOString().slice(0, 10)
  } catch { return iso }
}

interface DocumentDetailProps {
  detail: ReviewDocument | null
  loading: boolean
  submitting: boolean
  onSubmitReview: (action: ReviewAction, comment: string, scenarioType?: string) => Promise<void>
}

export function DocumentDetail({
  detail,
  loading,
  submitting,
  onSubmitReview,
}: DocumentDetailProps) {
  const [comment, setComment] = useState('')
  const [scenarioType, setScenarioType] = useState(detail?.scenario_type || '')
  const [actionFeedback, setActionFeedback] = useState<string | null>(null)

  if (!detail && !loading) {
    return (
      <section className="flex-1 flex flex-col overflow-hidden bg-white">
        <div className="flex-1 flex items-center justify-center" style={{ color: '#999', fontSize: 13 }}>
          点击左侧文档查看详情
        </div>
      </section>
    )
  }

  const handleAction = async (action: ReviewAction, label: string) => {
    setActionFeedback(label)
    try {
      await onSubmitReview(action, comment, scenarioType || undefined)
      if (action !== 'save_note') setComment('')
    } catch {
      // error handled upstream
    } finally {
      setActionFeedback(null)
    }
  }

  const risk = detail ? (RISK_STYLE[detail.risk_level] || RISK_STYLE['low']) : null
  const RiskIcon = risk?.icon
  const statusCfg = detail ? (STATUS_STYLE[detail.review_status] || STATUS_STYLE['pending_review']) : null
  const isPending = detail?.review_status === 'pending_review' || detail?.review_status === 'need_edit'

  return (
    <section className="flex-1 flex flex-col overflow-hidden bg-white">
      {loading ? (
        <div className="flex-1 p-6 space-y-4 animate-pulse">
          <div className="h-6 w-64 bg-gray-100 rounded" />
          <div className="h-4 w-48 bg-gray-100 rounded" />
          <div className="h-40 bg-gray-50 rounded-lg mt-4" />
        </div>
      ) : detail ? (
        <>
          {/* Document Info Header */}
          <div className="flex-shrink-0 px-6 pt-5 pb-3 border-b border-gray-100">
            <div className="flex items-start justify-between mb-2">
              <div className="min-w-0 flex-1">
                <h3
                  className="font-bold truncate"
                  style={{ fontSize: 18, color: '#1a1a2e', letterSpacing: '-0.01em' }}
                >
                  {detail.title}
                </h3>
                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                  {risk && RiskIcon && (
                    <span
                      className="status-badge"
                      style={{ background: risk.bg, color: risk.color, border: `1px solid ${risk.border}` }}
                    >
                      <RiskIcon size={10} style={{ marginRight: 3 }} />
                      {risk.label}
                    </span>
                  )}
                  <span className="inline-flex items-center gap-1" style={{ fontSize: 12, color: '#888' }}>
                    <User size={12} />
                    <span style={{ color: '#aaa' }}>提交者：</span>
                    {detail.submitter_name}
                  </span>
                  <span className="inline-flex items-center gap-1" style={{ fontSize: 12, color: '#888' }}>
                    <Clock size={12} />
                    <span style={{ color: '#aaa' }}>提交于：</span>
                    {formatDate(detail.created_at)}
                  </span>
                  <span className="inline-flex items-center gap-1" style={{ fontSize: 12, color: '#888' }}>
                    <FileText size={12} />
                    <span style={{ color: '#aaa' }}>编号：</span>
                    {detail.doc_no}
                  </span>
                </div>
              </div>
              {statusCfg && (
                <span
                  className="status-badge flex-shrink-0 ml-3"
                  style={{
                    background: statusCfg.bg,
                    color: statusCfg.color,
                    border: `1px solid ${statusCfg.border}`,
                    fontSize: 12,
                    padding: '4px 12px',
                  }}
                >
                  {statusCfg.label}
                </span>
              )}
            </div>
            {/* Show previous review comment if exists */}
            {detail.review_comment && (
              <div
                className="mt-2 p-2.5 rounded-md"
                style={{ background: '#fafafa', fontSize: 12, color: '#666', border: '1px solid #f0f0f0' }}
              >
                <span style={{ fontWeight: 500, color: '#888' }}>审核备注：</span>
                {detail.review_comment}
              </div>
            )}
          </div>

          {/* Document Content Preview */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            <h4 className="font-semibold mb-3" style={{ fontSize: 14, color: '#555' }}>
              文档内容预览
            </h4>
            <div
              className="doc-preview-block"
              style={{
                background: '#fafbfc',
                border: '1px solid #eee',
                borderRadius: 10,
                padding: '16px 18px',
                fontSize: 13,
                lineHeight: 1.7,
                color: '#444',
                maxHeight: 260,
                overflowY: 'auto',
              }}
            >
              {detail.content ? (
                <div style={{ whiteSpace: 'pre-wrap' }}>{detail.content}</div>
              ) : (
                <p style={{ color: '#999' }}>暂无内容</p>
              )}
            </div>

            {/* Tags */}
            {detail.tags && detail.tags.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-2" style={{ fontSize: 14, color: '#555' }}>
                  标签
                </h4>
                <div className="flex flex-wrap gap-2">
                  {detail.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="status-badge"
                      style={{ background: '#f5f5f5', color: '#666', border: '1px solid #e0e0e0' }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Review Actions */}
          {isPending && (
            <div className="flex-shrink-0 px-6 py-4 border-t border-gray-100" style={{ background: '#fafbfc' }}>
              {/* Scenario Type Selector */}
              <label className="block mb-2 font-medium" style={{ fontSize: 13, color: '#555' }}>
                场景分类
              </label>
              <div className="flex gap-2 mb-4">
                {[
                  { value: '售前咨询', label: '售前咨询', desc: '产品咨询、价格、功能等问题' },
                  { value: '售后服务', label: '售后服务', desc: '退换货、维修、投诉等问题' },
                ].map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    className="flex-1 px-3 py-2.5 rounded-lg text-sm font-medium transition-all"
                    style={{
                      border: scenarioType === opt.value
                        ? '2px solid #0066CC'
                        : '2px solid #e0e0e0',
                      background: scenarioType === opt.value
                        ? '#e6f4ff'
                        : '#fff',
                      color: scenarioType === opt.value ? '#0066CC' : '#888',
                    }}
                    onClick={() => setScenarioType(scenarioType === opt.value ? '' : opt.value)}
                  >
                    <div style={{ fontSize: 13 }}>{opt.label}</div>
                    <div style={{ fontSize: 10, color: scenarioType === opt.value ? '#0066CC' : '#aaa', marginTop: 2 }}>
                      {opt.desc}
                    </div>
                  </button>
                ))}
              </div>

              <label className="block mb-2 font-medium" style={{ fontSize: 13, color: '#555' }}>
                审核意见
              </label>
              <textarea
                className="review-textarea mb-4"
                style={{
                  width: '100%',
                  border: '1px solid #e0e0e0',
                  borderRadius: 8,
                  padding: '12px 14px',
                  fontSize: 13,
                  color: '#333',
                  resize: 'vertical',
                  minHeight: 80,
                  outline: 'none',
                  background: '#fafafa',
                  lineHeight: 1.6,
                }}
                placeholder="输入审核意见..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#0066CC'
                  e.currentTarget.style.background = '#fff'
                  e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0,102,204,0.08)'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#e0e0e0'
                  e.currentTarget.style.background = '#fafafa'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              />

              <div className="flex items-center gap-3">
                <button
                  className="flex-1 text-white"
                  style={{
                    background: '#0066CC',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                    fontSize: 13,
                    fontWeight: 500,
                    padding: '10px 16px',
                    borderRadius: 8,
                    cursor: 'pointer',
                    border: 'none',
                    transition: 'all 0.2s',
                  }}
                  disabled={submitting}
                  onClick={() => handleAction('approve', '批准')}
                >
                  <Check size={16} />
                  {actionFeedback === '批准' ? '处理中...' : '批准'}
                </button>
                <button
                  className="flex-1 text-white"
                  style={{
                    background: '#faad14',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                    fontSize: 13,
                    fontWeight: 500,
                    padding: '10px 16px',
                    borderRadius: 8,
                    cursor: 'pointer',
                    border: 'none',
                    transition: 'all 0.2s',
                  }}
                  disabled={submitting}
                  onClick={() => handleAction('request_changes', '需修改')}
                >
                  <Edit3 size={16} />
                  {actionFeedback === '需修改' ? '处理中...' : '需修改'}
                </button>
                <button
                  className="flex-1 text-white"
                  style={{
                    background: '#ff4d4f',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                    fontSize: 13,
                    fontWeight: 500,
                    padding: '10px 16px',
                    borderRadius: 8,
                    cursor: 'pointer',
                    border: 'none',
                    transition: 'all 0.2s',
                  }}
                  disabled={submitting}
                  onClick={() => handleAction('reject', '驳回')}
                >
                  <X size={16} />
                  {actionFeedback === '驳回' ? '处理中...' : '驳回'}
                </button>
                <button
                  className="flex-shrink-0 bg-white"
                  style={{
                    color: '#666',
                    border: '1px solid #d0d0d0',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                    fontSize: 13,
                    fontWeight: 500,
                    padding: '10px 16px',
                    borderRadius: 8,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  disabled={submitting}
                  onClick={() => handleAction('save_note', '保存备注')}
                >
                  <Save size={16} />
                  {actionFeedback === '保存备注' ? '保存中...' : '保存备注'}
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center" style={{ color: '#999', fontSize: 13 }}>
          无法加载文档详情
        </div>
      )}
    </section>
  )
}
