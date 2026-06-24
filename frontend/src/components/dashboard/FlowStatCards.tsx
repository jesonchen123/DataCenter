import type { FlowStatItem } from '@/types/dashboard'
import { FilePlus, Loader, Eye, CheckCircle } from 'lucide-react'

const ICON_MAP: Record<string, typeof FilePlus> = {
  'lucide:file-plus': FilePlus,
  'lucide:loader': Loader,
  'lucide:eye': Eye,
  'lucide:check-circle': CheckCircle,
}

const CONFIG: Record<string, { color: string; bg: string }> = {
  'lucide:file-plus': { color: '#0066CC', bg: 'rgba(0,102,204,0.08)' },
  'lucide:loader': { color: '#d48806', bg: 'rgba(250,173,20,0.08)' },
  'lucide:eye': { color: '#d48806', bg: 'rgba(250,173,20,0.08)' },
  'lucide:check-circle': { color: '#389e0d', bg: 'rgba(82,196,26,0.08)' },
}

export function FlowStatCards({ items }: { items: FlowStatItem[] }) {
  return (
    <div className="grid grid-cols-4 gap-5 mb-6">
      {items.map((item) => {
        const Icon = ICON_MAP[item.icon] || FilePlus
        const cfg = CONFIG[item.icon] || CONFIG['lucide:file-plus']
        const isActive = item.status === 'active' || item.status === 'warning'
        const isSuccess = item.status === 'success'

        return (
          <div
            key={item.label}
            className="card-hover bg-white rounded-xl p-5 shadow-sm border border-gray-100"
          >
            <div className="flex items-start justify-between mb-3">
              <div
                className="flex items-center justify-center rounded-lg"
                style={{ width: 40, height: 40, background: cfg.bg }}
              >
                <Icon size={20} color={cfg.color} />
              </div>

              {isActive && (
                <span
                  className="status-badge"
                  style={{ background: '#fff7e6', color: '#d48806', border: '1px solid #ffd591' }}
                >
                  <span
                    className="inline-block mr-1.5 w-1.5 h-1.5 rounded-full animate-pulse"
                    style={{ background: '#faad14' }}
                  />
                  进行中
                </span>
              )}
              {isSuccess && (
                <span
                  className="status-badge"
                  style={{ background: '#f6ffed', color: '#389e0d', border: '1px solid #b7eb8f' }}
                >
                  完成
                </span>
              )}
            </div>

            <p className="font-bold text-[32px] leading-none" style={{ color: '#1a1a2e' }}>
              {item.count}
            </p>
            <p className="text-[13px] mt-1" style={{ color: '#888' }}>
              {item.label}
            </p>
          </div>
        )
      })}
    </div>
  )
}
