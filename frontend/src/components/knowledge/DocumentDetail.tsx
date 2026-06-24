import { useState } from 'react'
import {
  AlertTriangle, AlertCircle, Info, User, Clock, FileText,
  Tag, Shield, BarChart3, History, Edit3, Send,
  CheckCircle, XCircle, AlertOctagon, Eye,
} from 'lucide-react'
import type { KnowledgeDocument, AuditEntry } from '@/types/knowledge'

const RISK_STYLE: Record<string, { bg: string; color: string; border: string; icon: typeof AlertTriangle; label: string }> = {
  high: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', icon: AlertTriangle, label: '高优先级' },
  medium: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', icon: AlertCircle, label: '中优先级' },
  low: { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', icon: Info, label: '低优先级' },
}

const STATUS_STYLE: Record<string, { bg: string; color: string; border: string; label: string; icon: typeof CheckCircle }> = {
  pending_review: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', label: '待审核', icon: AlertOctagon },
  need_edit: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', label: '需修改', icon: XCircle },
  approved: { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f', label: '已批准', icon: CheckCircle },
  rejected: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', label: '已驳回', icon: XCircle },
  archived: { bg: '#f5f5f5', color: '#999', border: '#e0e0e0', label: '已归档', icon: Eye },
}

const ACTION_LABELS: Record<string, string> = {
  created: '创建',
  updated: '编辑',
  submitted_for_review: '提交审核',
  approved: '审核通过',
  rejected: '审核驳回',
  review_request_changes: '需修改',
  review_note: '备注',
  desensitized: '脱敏',
  exported: '导出',
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toISOString().slice(0, 10)
  } catch { return iso }
}

function formatDateTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch { return iso }
}

const METADATA_FIELDS: { key: keyof KnowledgeDocument; label: string; booleanField?: boolean }[] = [
  { key: 'scenario_type', label: '场景类型' },
  { key: 'business_line', label: '业务线' },
  { key: 'product_name', label: '产品名称' },
  { key: 'quality_score', label: '质量分' },
  { key: 'price_filtered', label: '价格过滤', booleanField: true },
  { key: 'contains_price_intent', label: '含价格意图', booleanField: true },
  { key: 'contains_original_price', label: '含原始价格', booleanField: true },
  { key: 'is_desensitized', label: '已脱敏', booleanField: true },
]

interface DocumentDetailProps {
  detail: KnowledgeDocument | null
  loading: boolean
  updating: boolean
  onUpdate: (payload: Record<string, unknown>) => Promise<void>
  onSubmitReview: () => Promise<void>
}

export function DocumentDetail({
  detail,
  loading,
  updating,
  onUpdate,
  onSubmitReview,
}: DocumentDetailProps) {
  const [editMode, setEditMode] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editContent, setEditContent] = useState('')
  const [editTags, setEditTags] = useState('')

  if (!detail && !loading) {
    return (
      <section className="flex-1 flex flex-col overflow-hidden bg-white">
        <div className="flex-1 flex items-center justify-center" style={{ color: '#999', fontSize: 13 }}>
          点击左侧文档查看详情
        </div>
      </section>
    )
  }

  const risk = detail ? (RISK_STYLE[detail.risk_level] || RISK_STYLE['low']) : null
  const RiskIcon = risk?.icon
  const statusCfg = detail ? (STATUS_STYLE[detail.review_status] || STATUS_STYLE['pending_review']) : null
  const StatusIcon = statusCfg?.icon

  const enterEditMode = () => {
    if (!detail) return
    setEditTitle(detail.title)
    setEditContent(detail.content)
    setEditTags((detail.tags || []).join(', '))
    setEditMode(true)
  }

  const cancelEdit = () => setEditMode(false)

  const saveEdit = async () => {
    if (!detail) return
    const payload: Record<string, unknown> = {
      title: editTitle,
      content: editContent,
      tags: editTags.split(',').map((t) => t.trim()).filter(Boolean),
    }
    await onUpdate(payload)
    setEditMode(false)
  }

  const auditLogs: AuditEntry[] = detail?.audit_logs || []

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
              {editMode ? (
                <div className="flex-1 min-w-0">
                  <input
                    type="text"
                    className="w-full border border-gray-200 rounded-md px-3 py-1.5 text-sm outline-none"
                    style={{ fontSize: 18, fontWeight: 700, color: '#1a1a2e' }}
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#0066CC'
                      e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0,102,204,0.06)'
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = '#e0e0e0'
                      e.currentTarget.style.boxShadow = 'none'
                    }}
                  />
                </div>
              ) : (
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
                      <span style={{ color: '#aaa' }}>更新于：</span>
                      {formatDate(detail.updated_at)}
                    </span>
                    <span className="inline-flex items-center gap-1" style={{ fontSize: 12, color: '#888' }}>
                      <FileText size={12} />
                      <span style={{ color: '#aaa' }}>编号：</span>
                      {detail.doc_no}
                    </span>
                  </div>
                </div>
              )}
              {statusCfg && StatusIcon && (
                <span
                  className="status-badge flex-shrink-0 ml-3 flex items-center gap-1"
                  style={{
                    background: statusCfg.bg,
                    color: statusCfg.color,
                    border: `1px solid ${statusCfg.border}`,
                    fontSize: 12,
                    padding: '4px 12px',
                  }}
                >
                  <StatusIcon size={12} />
                  {statusCfg.label}
                </span>
              )}
            </div>
          </div>

          {/* Scrollable Content Area */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-5">
            {/* Content Preview */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold" style={{ fontSize: 14, color: '#555' }}>
                  文档内容
                </h4>
                {!editMode && (
                  <button
                    className="inline-flex items-center gap-1 text-xs font-medium cursor-pointer"
                    style={{ color: '#0066CC', border: 'none', background: 'transparent', padding: '2px 6px' }}
                    onClick={enterEditMode}
                  >
                    <Edit3 size={12} />
                    编辑
                  </button>
                )}
              </div>

              {editMode ? (
                <div className="space-y-3">
                  <textarea
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none resize-y"
                    style={{ minHeight: 160, fontSize: 13, color: '#333', lineHeight: 1.7 }}
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#0066CC'
                      e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0,102,204,0.06)'
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = '#e0e0e0'
                      e.currentTarget.style.boxShadow = 'none'
                    }}
                  />
                  <div>
                    <label className="block mb-1 font-medium" style={{ fontSize: 12, color: '#888' }}>
                      标签（逗号分隔）
                    </label>
                    <input
                      type="text"
                      className="w-full border border-gray-200 rounded-md px-3 py-1.5 text-sm outline-none"
                      style={{ fontSize: 13, color: '#333' }}
                      value={editTags}
                      onChange={(e) => setEditTags(e.target.value)}
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = '#0066CC'
                        e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0,102,204,0.06)'
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = '#e0e0e0'
                        e.currentTarget.style.boxShadow = 'none'
                      }}
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      className="px-4 py-1.5 rounded-md text-white text-xs font-medium cursor-pointer"
                      style={{ background: '#0066CC' }}
                      onClick={saveEdit}
                      disabled={updating}
                    >
                      {updating ? '保存中...' : '保存'}
                    </button>
                    <button
                      className="px-4 py-1.5 rounded-md text-xs font-medium cursor-pointer"
                      style={{ border: '1px solid #d0d0d0', background: '#fff', color: '#666' }}
                      onClick={cancelEdit}
                    >
                      取消
                    </button>
                  </div>
                </div>
              ) : (
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
                    maxHeight: 200,
                    overflowY: 'auto',
                  }}
                >
                  {detail.content ? (
                    <div style={{ whiteSpace: 'pre-wrap' }}>{detail.content}</div>
                  ) : (
                    <p style={{ color: '#999' }}>暂无内容</p>
                  )}
                </div>
              )}
            </div>

            {/* Tags */}
            {detail.tags && detail.tags.length > 0 && !editMode && (
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-1.5" style={{ fontSize: 14, color: '#555' }}>
                  <Tag size={13} />
                  标签
                </h4>
                <div className="flex flex-wrap gap-2">
                  {detail.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="status-badge"
                      style={{ background: '#f0f5ff', color: '#0066CC', border: '1px solid #d6e4ff', fontSize: 12 }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Metadata Grid */}
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-1.5" style={{ fontSize: 14, color: '#555' }}>
                <Shield size={13} />
                元数据
              </h4>
              <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                {METADATA_FIELDS.map(({ key, label, booleanField }) => {
                  const val = detail[key as keyof KnowledgeDocument]
                  let display: string
                  if (booleanField) {
                    display = val ? '是' : '否'
                  } else {
                    display = val != null ? String(val) : '-'
                  }
                  return (
                    <div
                      key={key}
                      className="flex items-center justify-between px-3 py-2 rounded-md"
                      style={{ background: '#fafbfc', border: '1px solid #f0f0f0' }}
                    >
                      <span style={{ fontSize: 12, color: '#888' }}>{label}</span>
                      <span
                        className="font-medium"
                        style={{
                          fontSize: 12,
                          color: booleanField && val ? '#389e0d' : booleanField && !val ? '#999' : '#333',
                        }}
                      >
                        {display}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Version History Timeline */}
            {auditLogs.length > 0 && (
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-1.5" style={{ fontSize: 14, color: '#555' }}>
                  <History size={13} />
                  版本历史
                </h4>
                <div className="relative pl-6">
                  {/* Vertical line */}
                  <div
                    className="absolute left-[5px] top-0 bottom-0 w-px"
                    style={{ background: '#e8e8e8' }}
                  />
                  <div className="space-y-3">
                    {auditLogs.map((entry, i) => (
                      <div key={entry.id || i} className="relative">
                        {/* Timeline dot */}
                        <div
                          className="absolute -left-6 top-1 timeline-dot"
                          style={{
                            width: 11,
                            height: 11,
                            borderRadius: '50%',
                            background: i === 0 ? '#0066CC' : '#d9d9d9',
                            boxShadow: i === 0 ? '0 0 0 3px rgba(0, 102, 204, 0.15)' : 'none',
                            border: '2px solid #fff',
                          }}
                        />
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium" style={{ fontSize: 12, color: '#333' }}>
                              {ACTION_LABELS[entry.action] || entry.action}
                            </span>
                            <span style={{ fontSize: 11, color: '#bbb' }}>
                              {entry.created_at ? formatDateTime(entry.created_at) : ''}
                            </span>
                          </div>
                          <p style={{ fontSize: 11, color: '#999', marginTop: 1 }}>
                            {entry.username}
                            {entry.detail?.summary ? ` — ${entry.detail.summary}` : ''}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          {!editMode && (
            <div className="flex-shrink-0 px-6 py-4 border-t border-gray-100 flex items-center gap-3" style={{ background: '#fafbfc' }}>
              <button
                className="inline-flex items-center gap-2 px-4 py-2 rounded-md text-white text-sm font-medium cursor-pointer"
                style={{ background: '#0066CC' }}
                onClick={enterEditMode}
              >
                <Edit3 size={14} />
                编辑文档
              </button>
              {detail.review_status === 'pending_review' || detail.review_status === 'need_edit' ? (
                <span className="inline-flex items-center gap-1" style={{ fontSize: 12, color: '#d48806' }}>
                  <AlertOctagon size={13} />
                  已在审核中
                </span>
              ) : (
                <button
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium cursor-pointer"
                  style={{ border: '1px solid #0066CC', color: '#0066CC', background: '#fff' }}
                  onClick={onSubmitReview}
                  disabled={updating}
                >
                  <Send size={14} />
                  {updating ? '提交中...' : '提交审核'}
                </button>
              )}
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
