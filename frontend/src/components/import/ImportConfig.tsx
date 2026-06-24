import { AlertTriangle, MinusCircle, Info } from 'lucide-react'

interface ImportConfigProps {
  category: string
  priority: string
  smartSplit: boolean
  autoMetadata: boolean
  onCategoryChange: (v: string) => void
  onPriorityChange: (v: string) => void
  onSmartSplitChange: (v: boolean) => void
  onAutoMetadataChange: (v: boolean) => void
  onApply: () => void
  onReset: () => void
}

const CATEGORIES = ['技术手册', '金融报告', '合规文件', '业务指南', '其他']

const PRIORITIES = [
  { value: '高', icon: AlertTriangle, color: '#ff4d4f', activeBg: '#fff1f0', activeColor: '#cf1322', activeBorder: '#ffa39e' },
  { value: '中', icon: MinusCircle, color: '#0066CC', activeBg: 'rgba(0,102,204,0.06)', activeColor: '#0066CC', activeBorder: '#0066CC' },
  { value: '低', icon: Info, color: '#91d5ff', activeBg: '#e6f7ff', activeColor: '#0066CC', activeBorder: '#91d5ff' },
]

export function ImportConfig({
  category,
  priority,
  smartSplit,
  autoMetadata,
  onCategoryChange,
  onPriorityChange,
  onSmartSplitChange,
  onAutoMetadataChange,
  onApply,
  onReset,
}: ImportConfigProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 className="font-semibold mb-4" style={{ fontSize: 15, color: '#1a1a2e' }}>
        配置导入参数
      </h3>

      {/* Document Category */}
      <div className="mb-4">
        <label
          className="block mb-2"
          style={{ fontSize: 12, color: '#666', fontWeight: 500 }}
        >
          文档类别
        </label>
        <select
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
          className="w-full px-3 py-2 rounded-lg border text-sm transition-colors outline-none"
          style={{
            borderColor: '#e0e0e0',
            color: '#333',
            fontSize: 13,
            background: '#fff',
            cursor: 'pointer',
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = '#0066CC'
            e.currentTarget.style.boxShadow = '0 0 0 2px rgba(0,102,204,0.08)'
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = '#e0e0e0'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {/* Priority */}
      <div className="mb-4">
        <label
          className="block mb-2"
          style={{ fontSize: 12, color: '#666', fontWeight: 500 }}
        >
          处理优先级
        </label>
        <div className="flex gap-2">
          {PRIORITIES.map((p) => {
            const active = priority === p.value
            const Icon = p.icon
            return (
              <label
                key={p.value}
                className="flex items-center gap-1.5 cursor-pointer px-3 py-2 rounded-lg border text-sm transition-all"
                style={{
                  borderColor: active ? p.activeBorder : '#e0e0e0',
                  fontSize: 13,
                  color: active ? p.activeColor : '#555',
                  background: active ? p.activeBg : '#fff',
                }}
              >
                <input
                  type="radio"
                  name="priority"
                  className="hidden"
                  checked={active}
                  onChange={() => onPriorityChange(p.value)}
                />
                <Icon size={13} />
                {p.value}
              </label>
            )
          })}
        </div>
      </div>

      {/* Toggle: Smart Split */}
      <div className="flex items-center justify-between mb-4 py-2">
        <div>
          <p style={{ fontSize: 13, color: '#333', fontWeight: 500 }}>启用智能分割</p>
          <p style={{ fontSize: 11, color: '#999' }}>自动识别文档章节边界</p>
        </div>
        <div
          className={`toggle-switch${smartSplit ? ' active' : ''}`}
          onClick={() => onSmartSplitChange(!smartSplit)}
        />
      </div>

      {/* Toggle: Auto Extract Metadata */}
      <div className="flex items-center justify-between mb-5 py-2">
        <div>
          <p style={{ fontSize: 13, color: '#333', fontWeight: 500 }}>自动提取元数据</p>
          <p style={{ fontSize: 11, color: '#999' }}>识别标题、作者、日期等字段</p>
        </div>
        <div
          className={`toggle-switch${autoMetadata ? ' active' : ''}`}
          onClick={() => onAutoMetadataChange(!autoMetadata)}
        />
      </div>

      {/* Buttons */}
      <div className="flex gap-3">
        <button
          className="flex-1 py-2.5 rounded-lg text-white font-medium text-sm transition-all hover:shadow-md"
          style={{ background: '#0066CC', fontSize: 13 }}
          onClick={onApply}
        >
          应用配置
        </button>
        <button
          className="px-5 py-2.5 rounded-lg font-medium text-sm transition-all"
          style={{ background: '#fff', border: '1px solid #e0e0e0', color: '#666', fontSize: 13 }}
          onClick={onReset}
        >
          重置
        </button>
      </div>
    </div>
  )
}
