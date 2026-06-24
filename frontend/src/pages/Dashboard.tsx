import { useDashboard } from '@/hooks/useDashboard'
import { FlowStatCards } from '@/components/dashboard/FlowStatCards'
import { TodoTable } from '@/components/dashboard/TodoTable'

export function Dashboard() {
  const { data, loading, error } = useDashboard()

  return (
    <>
      {/* Page Title */}
      <div className="mb-6">
        <h2 className="font-bold text-[22px] tracking-[-0.02em]" style={{ color: '#1a1a2e' }}>
          总览
        </h2>
        <p className="text-[13px] mt-0.5" style={{ color: '#999' }}>
          数据中台 · 全局概览 · 流程追踪
        </p>
      </div>

      {error && (
        <div
          className="mb-6 p-4 rounded-lg text-[13px]"
          style={{ background: '#fff1f0', color: '#cf1322', border: '1px solid #ffa39e' }}
        >
          加载失败：{error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-4 gap-5 mb-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 animate-pulse">
              <div className="h-10 w-10 rounded-lg bg-gray-100 mb-3" />
              <div className="h-8 w-16 bg-gray-100 rounded mb-1" />
              <div className="h-4 w-20 bg-gray-100 rounded" />
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* 1. Flow stat cards */}
          {data && <FlowStatCards items={data.flow_stats} />}

          {/* 2. TODO table */}
          {data && <TodoTable todos={data.todos} />}
        </>
      )}
    </>
  )
}
