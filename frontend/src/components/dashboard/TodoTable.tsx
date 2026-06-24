import type { TodoItem } from '@/types/dashboard'
import { AlertTriangle, AlertCircle, Info } from 'lucide-react'

const PRIORITY_STYLE: Record<string, { bg: string; color: string; border: string; icon: typeof AlertTriangle }> = {
  '高': { bg: '#fff1f0', color: '#cf1322', border: '#ffa39e', icon: AlertTriangle },
  '中': { bg: '#fff7e6', color: '#d48806', border: '#ffd591', icon: AlertCircle },
  '低': { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff', icon: Info },
}

const STATUS_STYLE: Record<string, { bg: string; color: string; border: string }> = {
  '进行中': { bg: '#e6f7ff', color: '#0066CC', border: '#91d5ff' },
  '待开始': { bg: '#fafafa', color: '#888', border: '#e0e0e0' },
  '已完成': { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f' },
}

function PriorityBadge({ priority }: { priority: string }) {
  const style = PRIORITY_STYLE[priority] || PRIORITY_STYLE['低']
  const Icon = style.icon
  return (
    <span className="status-badge" style={{ background: style.bg, color: style.color, border: `1px solid ${style.border}` }}>
      <Icon size={11} className="mr-1" />
      {priority}
    </span>
  )
}

function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLE[status] || STATUS_STYLE['待开始']
  return (
    <span className="status-badge" style={{ background: style.bg, color: style.color, border: `1px solid ${style.border}` }}>
      {status}
    </span>
  )
}

export function TodoTable({ todos }: { todos: TodoItem[] }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-[16px]" style={{ color: '#1a1a2e' }}>待办项目</h3>
        <a href="#" className="text-[13px] font-medium no-underline" style={{ color: '#0066CC' }}>
          查看全部 →
        </a>
      </div>
      <table className="w-full">
        <thead>
          <tr>
            <th style={{ width: 70 }}>优先级</th>
            <th>任务描述</th>
            <th style={{ width: 100 }}>指派人</th>
            <th style={{ width: 120 }}>截止日期</th>
            <th style={{ width: 90 }}>状态</th>
          </tr>
        </thead>
        <tbody>
          {todos.length === 0 ? (
            <tr>
              <td colSpan={5} className="text-center text-gray-400 py-8">暂无待办</td>
            </tr>
          ) : (
            todos.map((todo) => (
              <tr key={todo.id}>
                <td><PriorityBadge priority={todo.priority} /></td>
                <td className="font-medium">{todo.description}</td>
                <td>{todo.assignee}</td>
                <td style={{ color: todo.deadline ? '#ff4d4f' : '#999', fontWeight: 500 }}>
                  {todo.deadline || '—'}
                </td>
                <td><StatusBadge status={todo.status} /></td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
