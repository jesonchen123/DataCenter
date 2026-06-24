import type { ParsePreview } from '@/types/import'
import { FileSearch, CheckCircle, User, HeadsetIcon, Bot, Sparkles, FileCode } from 'lucide-react'

const ROLE_CONFIG: Record<string, { label: string; icon: typeof User; color: string; bg: string; border: string }> = {
  customer: {
    label: '客户',
    icon: User,
    color: '#0066CC',
    bg: '#e6f4ff',
    border: '#91caff',
  },
  staff: {
    label: '客服',
    icon: HeadsetIcon,
    color: '#389e0d',
    bg: '#f6ffed',
    border: '#b7eb8f',
  },
  system: {
    label: '系统',
    icon: Bot,
    color: '#8c8c8c',
    bg: '#fafafa',
    border: '#d9d9d9',
  },
  unknown: {
    label: '未知',
    icon: FileCode,
    color: '#999',
    bg: '#fafafa',
    border: '#e8e8e8',
  },
}

const NORMALIZER_LABELS: Record<string, { label: string; color: string; bg: string }> = {
  json_direct: { label: 'JSON 直接解析', color: '#389e0d', bg: '#f6ffed' },
  llm: { label: 'LLM 标准化', color: '#0066CC', bg: '#e6f4ff' },
  rule: { label: '规则解析', color: '#d48806', bg: '#fff7e6' },
  unknown: { label: '未知', color: '#999', bg: '#fafafa' },
}

interface ParsePreviewProps {
  preview: ParsePreview | null
  loading: boolean
}

export function ParsePreview({ preview, loading }: ParsePreviewProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col flex-1" style={{ minHeight: 360 }}>
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100 flex-shrink-0">
        <FileSearch size={18} color="#0066CC" />
        <h3 className="font-semibold" style={{ fontSize: 15, color: '#1a1a2e' }}>
          解析结果预览
        </h3>
      </div>

      {loading ? (
        <div className="space-y-3 p-5 animate-pulse flex-1">
          <div className="h-4 w-48 bg-gray-100 rounded" />
          <div className="h-4 w-32 bg-gray-100 rounded" />
          <div className="h-32 bg-gray-50 rounded-lg" />
          <div className="h-32 bg-gray-50 rounded-lg" />
        </div>
      ) : preview ? (
        <>
          {/* Metadata bar */}
          <div className="flex-shrink-0 px-5 py-3 border-b border-gray-100 flex flex-wrap items-center gap-2">
            {/* Filename */}
            <span style={{ fontSize: 12, color: '#333', fontWeight: 500 }}>
              {preview.filename}
            </span>

            {/* Import status */}
            <span
              className="status-badge"
              style={{
                background: preview.import_status === 'completed' ? '#f6ffed' : '#fff7e6',
                color: preview.import_status === 'completed' ? '#389e0d' : '#d48806',
                border: preview.import_status === 'completed' ? '1px solid #b7eb8f' : '1px solid #ffd591',
                fontSize: 10,
              }}
            >
              <CheckCircle size={10} style={{ marginRight: 3 }} />
              {preview.import_status === 'completed' ? '解析完成' : '解析中'}
            </span>

            {/* Normalizer badge */}
            {(() => {
              const nc = NORMALIZER_LABELS[preview.normalizer] || NORMALIZER_LABELS['unknown']
              return (
                <span
                  className="status-badge"
                  style={{ background: nc.bg, color: nc.color, border: `1px solid ${nc.color}20`, fontSize: 10 }}
                >
                  <Sparkles size={10} style={{ marginRight: 3 }} />
                  {nc.label}
                </span>
              )
            })()}

            {/* Role counts */}
            <span style={{ fontSize: 11, color: '#999', marginLeft: 'auto' }}>
              共 {preview.message_count} 条消息（客户 {preview.customer_count} · 客服 {preview.staff_count}）
            </span>
          </div>

          {/* Message list */}
          <div className="flex-1 overflow-y-auto px-5 py-3" style={{ maxHeight: 420 }}>
            {preview.messages.length === 0 ? (
              <p className="text-[13px] text-gray-400 py-8 text-center">无消息内容</p>
            ) : (
              <div className="flex flex-col gap-2.5">
                {preview.messages.map((msg, idx) => {
                  const isCustomer = msg.sender_role === 'customer'
                  const cfg = ROLE_CONFIG[msg.sender_role] || ROLE_CONFIG['unknown']
                  const RoleIcon = cfg.icon

                  return (
                    <div
                      key={msg.message_id || idx}
                      className="flex"
                      style={{ justifyContent: isCustomer ? 'flex-end' : 'flex-start' }}
                    >
                      <div style={{ maxWidth: '82%' }}>
                        {/* Role badge + sender name */}
                        <div
                          className="flex items-center gap-1.5 mb-1"
                          style={{ justifyContent: isCustomer ? 'flex-end' : 'flex-start' }}
                        >
                          <span
                            className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium"
                            style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}` }}
                          >
                            <RoleIcon size={10} />
                            {cfg.label}
                          </span>
                          {msg.sender_name && (
                            <span style={{ fontSize: 10, color: '#999' }}>{msg.sender_name}</span>
                          )}
                          <span style={{ fontSize: 10, color: '#bbb' }}>#{idx + 1}</span>
                        </div>

                        {/* Message bubble */}
                        <div
                          className="rounded-lg px-3.5 py-2.5"
                          style={{
                            background: isCustomer ? '#e6f4ff' : '#f5f5f5',
                            border: isCustomer ? '1px solid #bae0ff' : '1px solid #e8e8e8',
                            fontSize: 12,
                            color: '#333',
                            lineHeight: 1.65,
                            wordBreak: 'break-word',
                            whiteSpace: 'pre-wrap',
                          }}
                        >
                          {msg.content}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </>
      ) : (
        <p className="text-[13px] text-gray-400 py-8 text-center flex-1">
          点击左侧文件列表中的文件查看解析预览
        </p>
      )}
    </div>
  )
}
