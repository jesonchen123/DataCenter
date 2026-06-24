import type { TaskStats } from '@/types/processTask'

const CARDS: {
  key: keyof TaskStats
  label: string
  color: string
}[] = [
  { key: 'total', label: '任务总数', color: '#1a1a2e' },
  { key: 'running', label: '处理中', color: '#0066CC' },
  { key: 'completed', label: '已完成', color: '#389e0d' },
  { key: 'retrying', label: '重试中', color: '#d48806' },
  { key: 'failed', label: '失败', color: '#cf1322' },
]

export function StatsRow({ stats }: { stats: TaskStats | null }) {
  if (!stats) {
    return (
      <div className="grid grid-cols-5 gap-4 mb-6">
        {CARDS.map((c) => (
          <div
            key={c.key}
            className="bg-white rounded-lg px-4 py-3 border border-gray-100 shadow-sm animate-pulse"
          >
            <div className="h-3 w-12 bg-gray-100 rounded mb-2" />
            <div className="h-7 w-8 bg-gray-100 rounded" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-5 gap-4 mb-6">
      {CARDS.map((c) => (
        <div
          key={c.key}
          className="bg-white rounded-lg px-4 py-3 border border-gray-100 shadow-sm"
        >
          <p style={{ fontSize: 11, color: '#999' }}>{c.label}</p>
          <p
            className="font-bold"
            style={{ fontSize: 24, color: c.color }}
          >
            {stats[c.key]}
          </p>
        </div>
      ))}
    </div>
  )
}
