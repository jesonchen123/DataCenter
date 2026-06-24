import { Search, AlertTriangle, AlertCircle, Info, Clock } from 'lucide-react'
import type { ReviewDocument } from '@/types/review'

const RISK_STYLE: Record<string, { bg: string; color: string; border: string; icon: typeof AlertTriangle; label: string }> = {
  high: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', icon: AlertTriangle, label: '高' },
  medium: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', icon: AlertCircle, label: '中' },
  low: { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', icon: Info, label: '低' },
}

const STATUS_STYLE: Record<string, { bg: string; color: string; border: string; label: string }> = {
  pending_review: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', label: '待审' },
  need_edit: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', label: '需修改' },
  approved: { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f', label: '已批准' },
  rejected: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', label: '已驳回' },
}

function sinceText(iso: string): string {
  try {
    const diff = Date.now() - new Date(iso).getTime()
    const days = Math.floor(diff / 86400000)
    if (days >= 1) return `${days} 天前`
    const hours = Math.floor(diff / 3600000)
    if (hours >= 1) return `${hours} 小时前`
    return '刚刚'
  } catch { return iso }
}

interface DocumentListProps {
  docs: ReviewDocument[]
  total: number
  loading: boolean
  error: string | null
  selectedId: string | null
  search: string
  riskFilter: string
  statusFilter: string
  onSearchChange: (v: string) => void
  onRiskFilterChange: (v: string) => void
  onStatusFilterChange: (v: string) => void
  onSelect: (id: string) => void
}

export function DocumentList({
  docs,
  total,
  loading,
  error,
  selectedId,
  search,
  riskFilter,
  statusFilter,
  onSearchChange,
  onRiskFilterChange,
  onStatusFilterChange,
  onSelect,
}: DocumentListProps) {
  return (
    <section className="flex-shrink-0 flex flex-col bg-white border-r border-gray-200 h-full" style={{ width: '45%' }}>
      {/* Panel Header */}
      <div className="flex-shrink-0 px-5 pt-5 pb-3 border-b border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold" style={{ fontSize: 18, color: '#1a1a2e', letterSpacing: '-0.02em' }}>
            待审核文档
          </h2>
          {total > 0 && (
            <span
              className="flex items-center justify-center rounded-full font-semibold"
              style={{ width: 24, height: 24, fontSize: 12, background: '#faad14', color: '#1a1a2e' }}
            >
              {total}
            </span>
          )}
        </div>

        {/* Search */}
        <div className="relative mb-3">
          <Search
            size={15}
            color="#bbb"
            className="absolute left-3 top-1/2"
            style={{ transform: 'translateY(-50%)' }}
          />
          <input
            type="text"
            className="w-full border border-gray-200 rounded-lg text-sm outline-none transition-colors bg-gray-50 focus:bg-white"
            style={{ padding: '8px 12px 8px 36px', fontSize: 13, color: '#333' }}
            placeholder="搜索文档名称、提交者..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
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

        {/* Filter Chips */}
        <div className="flex items-center gap-2 flex-wrap">
          <FilterChip label="全部" value="" current={riskFilter} onChange={onRiskFilterChange} />
          <FilterChip
            label="高优先"
            value="high"
            current={riskFilter}
            onChange={onRiskFilterChange}
            dotColor="#ff4d4f"
          />
          <FilterChip
            label="中优先"
            value="medium"
            current={riskFilter}
            onChange={onRiskFilterChange}
            dotColor="#faad14"
          />
          <FilterChip
            label="低优先"
            value="low"
            current={riskFilter}
            onChange={onRiskFilterChange}
            dotColor="#0066CC"
          />
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-8 text-center animate-pulse" style={{ fontSize: 13, color: '#999' }}>
            加载中...
          </div>
        ) : error ? (
          <div className="p-8 text-center" style={{ fontSize: 13, color: '#cf1322' }}>
            {error}
          </div>
        ) : docs.length === 0 ? (
          <div className="p-8 text-center" style={{ fontSize: 13, color: '#999' }}>
            暂无待审核文档
          </div>
        ) : (
          docs.map((doc) => {
            const risk = RISK_STYLE[doc.risk_level] || RISK_STYLE['low']
            const RiskIcon = risk.icon
            const statusCfg = STATUS_STYLE[doc.review_status] || STATUS_STYLE['pending_review']
            const isSelected = selectedId === doc.id

            return (
              <div
                key={doc.id}
                className={`review-list-item flex items-center gap-3 ${isSelected ? 'selected' : ''}`}
                style={{
                  padding: '14px 16px',
                  borderBottom: '1px solid #f0f0f0',
                  cursor: 'pointer',
                  transition: 'background 0.15s ease',
                  background: isSelected ? '#e6f4ff' : undefined,
                  borderLeft: isSelected ? '3px solid #0066CC' : '3px solid transparent',
                  paddingLeft: isSelected ? 13 : 16,
                }}
                onClick={() => onSelect(doc.id)}
                onMouseEnter={(e) => {
                  if (!isSelected) e.currentTarget.style.background = '#f5f8ff'
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) e.currentTarget.style.background = ''
                }}
              >
                {/* Risk badge */}
                <span
                  className="status-badge flex-shrink-0"
                  style={{ background: risk.bg, color: risk.color, border: `1px solid ${risk.border}` }}
                >
                  <RiskIcon size={10} style={{ marginRight: 3 }} />
                  {risk.label}
                </span>

                {/* Doc info */}
                <div className="flex-1 min-w-0">
                  <p className="font-semibold truncate" style={{ fontSize: 13.5, color: '#1a1a2e' }}>
                    {doc.title}
                  </p>
                  <div className="flex items-center gap-1 mt-0.5" style={{ fontSize: 11, color: '#999' }}>
                    <span>{doc.submitter_name}</span>
                    <span style={{ color: '#ddd' }}>·</span>
                    <Clock size={10} style={{ marginRight: -2 }} />
                    <span>{sinceText(doc.created_at)}</span>
                  </div>
                </div>

                {/* Status badge */}
                <span
                  className="status-badge flex-shrink-0"
                  style={{ background: statusCfg.bg, color: statusCfg.color, border: `1px solid ${statusCfg.border}` }}
                >
                  {statusCfg.label}
                </span>
              </div>
            )
          })
        )}
      </div>
    </section>
  )
}

function FilterChip({
  label,
  value,
  current,
  onChange,
  dotColor,
}: {
  label: string
  value: string
  current: string
  onChange: (v: string) => void
  dotColor?: string
}) {
  const active = current === value
  return (
    <button
      className="filter-chip"
      style={{
        padding: '5px 12px',
        borderRadius: 6,
        fontSize: 12,
        fontWeight: 500,
        cursor: 'pointer',
        border: active ? '1px solid #0066CC' : '1px solid #e0e0e0',
        background: active ? '#0066CC' : '#fff',
        color: active ? '#fff' : '#666',
        transition: 'all 0.15s ease',
        whiteSpace: 'nowrap',
      }}
      onClick={() => onChange(value)}
      onMouseEnter={(e) => {
        if (!active) {
          e.currentTarget.style.borderColor = '#0066CC'
          e.currentTarget.style.color = '#0066CC'
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.currentTarget.style.borderColor = '#e0e0e0'
          e.currentTarget.style.color = '#666'
        }
      }}
    >
      {dotColor && (
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: dotColor,
            display: 'inline-block',
            marginRight: 4,
          }}
        />
      )}
      {label}
    </button>
  )
}
