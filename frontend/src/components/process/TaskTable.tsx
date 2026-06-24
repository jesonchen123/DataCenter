import { Search } from 'lucide-react'
import type { ProcessTask } from '@/types/processTask'
import {
  CheckCircle,
  XCircle,
  RefreshCw,
  Loader,
} from 'lucide-react'

/* ── stage map ─────────────────────────────────── */
const STAGE_STYLE: Record<string, { bg: string; color: string; border: string; label: string }> = {
  parse: { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', label: '解析' },
  clean: { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', label: '清洗' },
  segment: { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', label: '分段' },
  desensitize: { bg: '#f9f0ff', color: '#722ed1', border: '#d3adf7', label: '脱敏' },
  price_filter: { bg: '#f9f0ff', color: '#722ed1', border: '#d3adf7', label: '价格过滤' },
  generate_knowledge: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', label: '生成知识' },
  review: { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f', label: '审核' },
  validate: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', label: '验证' },
}

const STATUS_STYLE: Record<string, {
  bg: string; color: string; border: string; label: string
  icon: typeof CheckCircle
}> = {
  completed: { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f', label: '成功', icon: CheckCircle },
  success: { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f', label: '待提交', icon: CheckCircle },
  running: { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', label: '处理中', icon: Loader },
  pending: { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', label: '处理中', icon: Loader },
  retrying: { bg: '#fff7e6', color: '#d48806', border: '#ffd591', label: '重试', icon: RefreshCw },
  failed: { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', label: '失败', icon: XCircle },
}

function progressColor(pct: number): string {
  if (pct >= 90) return '#52c41a'
  if (pct >= 60) return '#faad14'
  return '#ff4d4f'
}

interface TaskTableProps {
  tasks: ProcessTask[]
  total: number
  page: number
  pageSize: number
  loading: boolean
  error: string | null
  selectedId: string | null
  search: string
  stageFilter: string
  statusFilter: string
  onSearchChange: (v: string) => void
  onStageFilterChange: (v: string) => void
  onStatusFilterChange: (v: string) => void
  onSelect: (id: string) => void
  onPageChange: (p: number) => void
}

export function TaskTable({
  tasks,
  total,
  page,
  pageSize,
  loading,
  error,
  selectedId,
  search,
  stageFilter,
  statusFilter,
  onSearchChange,
  onStageFilterChange,
  onStatusFilterChange,
  onSelect,
  onPageChange,
}: TaskTableProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      {/* header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
        <h3 className="font-semibold" style={{ fontSize: 16, color: '#1a1a2e' }}>
          任务列表
        </h3>
        <div className="flex items-center gap-3">
          {/* search */}
          <div className="relative">
            <input
              type="text"
              placeholder="搜索任务或文档..."
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
              style={{ width: 200, outline: 'none', fontSize: 13, color: '#333' }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#0066CC'
                e.currentTarget.style.boxShadow = '0 0 0 2px rgba(0,102,204,0.08)'
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = '#d0d0d0'
                e.currentTarget.style.boxShadow = 'none'
              }}
            />
            <Search
              size={14}
              color="#999"
              className="absolute right-3 top-1/2"
              style={{ transform: 'translateY(-50%)' }}
            />
          </div>

          {/* stage filter */}
          <select
            value={stageFilter}
            onChange={(e) => onStageFilterChange(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
            style={{ outline: 'none', fontSize: 13, color: '#555', cursor: 'pointer' }}
          >
            <option value="">全部阶段</option>
            <option value="parse">解析</option>
            <option value="validate">验证</option>
            <option value="review">审核</option>
            <option value="clean">清洗</option>
            <option value="desensitize">脱敏</option>
          </select>

          {/* status filter */}
          <select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
            style={{ outline: 'none', fontSize: 13, color: '#555', cursor: 'pointer' }}
          >
            <option value="">所有状态</option>
            <option value="completed">成功</option>
            <option value="success">待提交</option>
            <option value="retrying">重试</option>
            <option value="failed">失败</option>
            <option value="running">处理中</option>
            <option value="pending">等待中</option>
          </select>
        </div>
      </div>

      {/* table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr>
              <th style={{ width: 110 }}>任务 ID</th>
              <th>文档名称</th>
              <th style={{ width: 110 }}>处理阶段</th>
              <th style={{ width: 150 }}>成功率</th>
              <th style={{ width: 120 }}>LLM 状态</th>
              <th style={{ width: 90 }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center text-gray-400 py-12 animate-pulse">
                  加载中...
                </td>
              </tr>
            ) : error ? (
              <tr>
                <td colSpan={6} className="text-center py-12" style={{ color: '#cf1322', fontSize: 13 }}>
                  {error}
                </td>
              </tr>
            ) : tasks.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center text-gray-400 py-12">
                  暂无任务数据
                </td>
              </tr>
            ) : (
              tasks.map((task) => {
                const stage = STAGE_STYLE[task.current_step || ''] || {
                  bg: '#fafafa', color: '#888', border: '#e0e0e0', label: task.current_step || '排队中',
                }
                const statusCfg = STATUS_STYLE[task.status] || STATUS_STYLE['pending']
                const StatusIcon = statusCfg.icon
                const pColor = progressColor(task.progress)
                const isSelected = selectedId === task.id

                return (
                  <tr
                    key={task.id}
                    onClick={() => onSelect(task.id)}
                    style={{ cursor: 'pointer', background: isSelected ? '#e6f0ff' : undefined }}
                  >
                    <td style={{ color: '#0066CC', fontWeight: 500 }}>
                      #{task.task_no.slice(-5)}
                    </td>
                    <td style={{ fontWeight: 500 }}>{task.doc_name}</td>
                    <td>
                      <span
                        className="status-badge"
                        style={{
                          background: stage.bg,
                          color: stage.color,
                          border: `1px solid ${stage.border}`,
                        }}
                      >
                        {stage.label}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="progress-bar flex-1">
                          <div
                            className="progress-fill"
                            style={{ width: `${task.progress}%`, background: pColor }}
                          />
                        </div>
                        <span style={{ fontSize: 12, color: pColor, fontWeight: 600 }}>
                          {task.progress}%
                        </span>
                      </div>
                    </td>
                    <td>
                      <span
                        className="status-badge"
                        style={{
                          background: statusCfg.bg,
                          color: statusCfg.color,
                          border: `1px solid ${statusCfg.border}`,
                        }}
                      >
                        <StatusIcon size={12} style={{ marginRight: 3 }} />
                        {statusCfg.label}
                        {task.status === 'retrying' && ` (${task.retry_count}/3)`}
                      </span>
                    </td>
                    <td>
                      <span
                        className="cursor-pointer"
                        style={{ fontSize: 12, color: '#0066CC', fontWeight: 500 }}
                        onClick={(e) => {
                          e.stopPropagation()
                          onSelect(task.id)
                        }}
                      >
                        查看详情
                      </span>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* pagination */}
      <div className="flex items-center justify-between px-6 py-3 border-t border-gray-100">
        <span style={{ fontSize: 13, color: '#888' }}>
          显示 {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, total)} 条，共 {total} 条
        </span>
        <div className="flex items-center gap-2">
          <button
            className="border border-gray-200 rounded-md px-3 py-1.5 text-sm"
            style={{ color: page <= 1 ? '#ccc' : '#555', cursor: page <= 1 ? 'default' : 'pointer' }}
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            上一页
          </button>
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
            let pageNum: number
            if (totalPages <= 5) {
              pageNum = i + 1
            } else if (page <= 3) {
              pageNum = i + 1
            } else if (page >= totalPages - 2) {
              pageNum = totalPages - 4 + i
            } else {
              pageNum = page - 2 + i
            }
            return (
              <button
                key={pageNum}
                className="rounded-md px-3 py-1.5 text-sm"
                style={{
                  background: pageNum === page ? '#0066CC' : 'transparent',
                  color: pageNum === page ? '#fff' : '#555',
                  border: pageNum === page ? 'none' : '1px solid #e0e0e0',
                  cursor: 'pointer',
                }}
                onClick={() => onPageChange(pageNum)}
              >
                {pageNum}
              </button>
            )
          })}
          <button
            className="border border-gray-200 rounded-md px-3 py-1.5 text-sm"
            style={{
              color: page >= totalPages ? '#ccc' : '#555',
              cursor: page >= totalPages ? 'default' : 'pointer',
            }}
            disabled={page >= totalPages}
            onClick={() => onPageChange(page + 1)}
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  )
}
