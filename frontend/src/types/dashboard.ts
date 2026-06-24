/* Dashboard API response types */

export interface FlowStatItem {
  label: string
  count: number
  icon: string
  status: 'active' | 'warning' | 'success'
}

export interface TodoItem {
  id: string
  priority: '高' | '中' | '低'
  description: string
  assignee: string
  deadline: string | null
  status: string
}

export interface RiskAlert {
  id: string
  severity: '严重' | '警告'
  title: string
  detail: string
  task_ids: string[]
}

export interface RecentTask {
  id: string
  task_no: string
  doc_name: string
  stage: string
  progress: number
  status: string
}

export interface DashboardSummary {
  flow_stats: FlowStatItem[]
  todos: TodoItem[]
  risk_alerts: RiskAlert[]
  recent_tasks: RecentTask[]
}
