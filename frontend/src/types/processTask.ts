export interface TaskStats {
  total: number
  running: number
  completed: number
  retrying: number
  failed: number
}

export interface ProcessTask {
  id: string
  task_no: string
  mock_chat_id: string
  triggered_by: string
  status: 'pending' | 'running' | 'completed' | 'success' | 'retrying' | 'failed'
  current_step: string | null
  progress: number
  error_message: string | null
  retry_count: number
  step_result: Record<string, unknown> | null
  doc_name: string
  doc_category: string
  assignee_name: string
  created_at: string
  updated_at: string
  completed_at: string | null
}

export interface TaskLog {
  id: string
  related_type: string | null
  related_id: string | null
  provider: string | null
  model_name: string | null
  status: string
  error_message: string | null
  latency_ms: number | null
  parsed_output: Record<string, unknown> | null
  created_at: string
}

export interface TaskListResponse {
  items: ProcessTask[]
  total: number
  page: number
  page_size: number
}

/** Timeline step derived from step_result */
export interface TimelineStep {
  label: string          // e.g. "文档上传", "文档解析", "内容验证", "审核提交"
  status: 'completed' | 'active' | 'pending'
  time: string | null
  description: string | null
}

/** Success rate breakdown */
export interface SuccessRates {
  parse: number | null      // 0-100
  validate: number | null
  review: number | null
}
