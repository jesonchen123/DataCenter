import type { RiskAlert } from '@/types/dashboard'
import { AlertTriangle, XCircle, Clock } from 'lucide-react'

const SEVERITY_ICON: Record<string, typeof AlertTriangle> = {
  '严重': XCircle,
  '警告': AlertTriangle,
}

const SEVERITY_BADGE: Record<string, { bg: string; color: string; border: string }> = {
  '严重': { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e' },
  '警告': { bg: '#fff7e6', color: '#d48806', border: '#ffd591' },
}

const SEVERITY_COLOR: Record<string, string> = {
  '严重': '#ff4d4f',
  '警告': '#faad14',
}

export function RiskAlerts({ alerts }: { alerts: RiskAlert[] }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle size={20} color="#ff4d4f" />
        <h3 className="font-semibold text-[16px]" style={{ color: '#1a1a2e' }}>风险提醒</h3>
        <span
          className="ml-auto flex items-center justify-center rounded-full text-white w-[22px] h-[22px] text-[11px] font-semibold"
          style={{ background: '#ff4d4f' }}
        >
          {alerts.length}
        </span>
      </div>

      {alerts.length === 0 ? (
        <p className="text-[13px] text-gray-400 py-4 text-center">暂无风险提醒</p>
      ) : (
        alerts.map((alert) => {
          const Icon = SEVERITY_ICON[alert.severity] || AlertTriangle
          const color = SEVERITY_COLOR[alert.severity] || '#faad14'
          const badge = SEVERITY_BADGE[alert.severity] || SEVERITY_BADGE['警告']

          return (
            <div key={alert.id} className="risk-item flex gap-3 mb-2.5">
              <div className="flex-shrink-0 mt-0.5">
                <Icon size={16} color={color} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[13px] font-medium leading-[1.4]" style={{ color: '#333' }}>
                  {alert.title}
                </p>
                <p className="text-xs mt-0.5" style={{ color: '#999' }}>
                  {alert.detail}
                </p>
                <span
                  className="inline-block mt-2 status-badge text-[11px]"
                  style={{ background: badge.bg, color: badge.color, border: `1px solid ${badge.border}` }}
                >
                  {alert.severity}
                </span>
              </div>
            </div>
          )
        })
      )}
    </div>
  )
}
