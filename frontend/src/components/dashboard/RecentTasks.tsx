import type { RecentTask } from '@/types/dashboard'

const STAGE_BADGE: Record<string, { bg: string; color: string; border: string }> = {
  '解析': { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff' },
  '清洗': { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff' },
  '分段': { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff' },
  '脱敏': { bg: '#f9f0ff', color: '#722ed1', border: '#d3adf7' },
  '价格过滤': { bg: '#f9f0ff', color: '#722ed1', border: '#d3adf7' },
  '生成知识': { bg: '#fff7e6', color: '#d48806', border: '#ffd591' },
  '审核': { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f' },
  '导出': { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f' },
  '失败': { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e' },
  '完成': { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f' },
  '处理中': { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff' },
}

function progressColor(pct: number): string {
  if (pct >= 90) return '#52c41a'
  if (pct >= 60) return '#faad14'
  return '#0066CC'
}

export function RecentTasks({ tasks }: { tasks: RecentTask[] }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-[16px]" style={{ color: '#1a1a2e' }}>近期任务</h3>
        <a href="#" className="text-[13px] font-medium no-underline" style={{ color: '#0066CC' }}>
          查看全部 →
        </a>
      </div>
      <table className="w-full">
        <thead>
          <tr>
            <th style={{ width: 80 }}>任务 ID</th>
            <th>文档名称</th>
            <th style={{ width: 80 }}>处理阶段</th>
            <th style={{ width: 120 }}>进度</th>
            <th style={{ width: 80 }}>操作</th>
          </tr>
        </thead>
        <tbody>
          {tasks.length === 0 ? (
            <tr>
              <td colSpan={5} className="text-center text-gray-400 py-8">暂无近期任务</td>
            </tr>
          ) : (
            tasks.map((task) => {
              const badge = STAGE_BADGE[task.stage] || STAGE_BADGE['处理中']
              const pColor = progressColor(task.progress)
              return (
                <tr key={task.id}>
                  <td className="font-medium" style={{ color: '#0066CC' }}>#{task.task_no}</td>
                  <td className="font-medium">{task.doc_name}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ background: badge.bg, color: badge.color, border: `1px solid ${badge.border}` }}
                    >
                      {task.stage}
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
                      <span className="text-[12px] font-semibold" style={{ color: pColor }}>
                        {task.progress}%
                      </span>
                    </div>
                  </td>
                  <td>
                    <a
                      href={`#/tasks/${task.id}`}
                      className="text-[12px] font-medium no-underline"
                      style={{ color: '#0066CC' }}
                    >
                      查看详情
                    </a>
                  </td>
                </tr>
              )
            })
          )}
        </tbody>
      </table>
    </div>
  )
}
