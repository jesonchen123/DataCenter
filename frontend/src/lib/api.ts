import type { DashboardSummary } from '@/types/dashboard'
import type { ImportFile, ParsePreview, UploadResult } from '@/types/import'
import type { TaskStats, TaskListResponse, ProcessTask, TaskLog } from '@/types/processTask'

const BASE_URL = '/api/v1'

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    // Extract error detail from the JSON response body (FastAPI returns {"detail": "..."})
    let detail = `${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      if (body?.detail) detail = body.detail
    } catch {
      // Response body is not JSON — use default status text
    }
    throw new Error(detail)
  }
  return res.json()
}

// ── Dashboard ──────────────────────────────────

export function fetchDashboardSummary(): Promise<DashboardSummary> {
  return fetchJSON<DashboardSummary>(`${BASE_URL}/dashboard/summary`)
}

// ── Document Import ────────────────────────────

export function fetchImportFiles(): Promise<ImportFile[]> {
  return fetchJSON<ImportFile[]>(`${BASE_URL}/mock-chats`)
}

export function fetchParsePreview(mockChatId: string): Promise<ParsePreview> {
  return fetchJSON<ParsePreview>(`${BASE_URL}/mock-chats/${mockChatId}/preview`)
}

export async function uploadDocument(formData: FormData): Promise<UploadResult> {
  return fetchJSON<UploadResult>(`${BASE_URL}/mock-chats/upload`, {
    method: 'POST',
    body: formData,
  })
}

export function deleteImportFile(mockChatId: string): Promise<void> {
  return fetchJSON<void>(`${BASE_URL}/mock-chats/${mockChatId}`, {
    method: 'DELETE',
  })
}

export function triggerProcessTask(mockChatId: string): Promise<{
  id: string
  task_no: string
  status: string
  current_step: string | null
  progress: number
}> {
  return fetchJSON(`${BASE_URL}/mock-chats/${mockChatId}/process`, {
    method: 'POST',
  })
}

// ── Process Tasks ───────────────────────────────

export interface TaskListParams {
  search?: string
  stage?: string
  status?: string
  page?: number
  page_size?: number
}

export function fetchTaskStats(): Promise<TaskStats> {
  return fetchJSON<TaskStats>(`${BASE_URL}/process-tasks/stats`)
}

export function fetchProcessTasks(params: TaskListParams = {}): Promise<TaskListResponse> {
  const qs = new URLSearchParams()
  if (params.search) qs.set('search', params.search)
  if (params.stage) qs.set('stage', params.stage)
  if (params.status) qs.set('status', params.status)
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return fetchJSON<TaskListResponse>(`${BASE_URL}/process-tasks${suffix}`)
}

export function fetchTaskDetail(processTaskId: string): Promise<ProcessTask> {
  return fetchJSON<ProcessTask>(`${BASE_URL}/process-tasks/${processTaskId}`)
}

export function fetchTaskLogs(processTaskId: string): Promise<TaskLog[]> {
  return fetchJSON<TaskLog[]>(`${BASE_URL}/process-tasks/${processTaskId}/logs`)
}

export function submitTaskToReview(processTaskId: string): Promise<ProcessTask & { doc_count: number }> {
  return fetchJSON<ProcessTask & { doc_count: number }>(
    `${BASE_URL}/process-tasks/${processTaskId}/submit-review`,
    { method: 'POST' },
  )
}

// ── Knowledge Base ────────────────────────────────

import type { KnowledgeStats, KnowledgeListResponse, KnowledgeDocument } from '@/types/knowledge'

export interface KnowledgeListParams {
  search?: string
  scenario_type?: string
  risk_level?: string
  review_status?: string
  page?: number
  page_size?: number
}

export function fetchKnowledgeStats(): Promise<KnowledgeStats> {
  return fetchJSON<KnowledgeStats>(`${BASE_URL}/knowledge-base/stats`)
}

export function fetchKnowledgeDocuments(params: KnowledgeListParams = {}): Promise<KnowledgeListResponse> {
  const qs = new URLSearchParams()
  if (params.search) qs.set('search', params.search)
  if (params.scenario_type) qs.set('scenario_type', params.scenario_type)
  if (params.risk_level) qs.set('risk_level', params.risk_level)
  if (params.review_status) qs.set('review_status', params.review_status)
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return fetchJSON<KnowledgeListResponse>(`${BASE_URL}/knowledge-base/documents${suffix}`)
}

export function fetchKnowledgeDetail(docId: string): Promise<KnowledgeDocument> {
  return fetchJSON<KnowledgeDocument>(`${BASE_URL}/knowledge-base/documents/${docId}`)
}

export function updateKnowledgeDocument(docId: string, payload: Record<string, unknown>): Promise<KnowledgeDocument> {
  return fetchJSON<KnowledgeDocument>(`${BASE_URL}/knowledge-base/documents/${docId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function submitKnowledgeForReview(docId: string): Promise<KnowledgeDocument> {
  return fetchJSON<KnowledgeDocument>(`${BASE_URL}/knowledge-base/documents/${docId}/submit-review`, {
    method: 'POST',
  })
}

// ── Review Center ────────────────────────────────

import type { ReviewStats, ReviewListResponse, ReviewDocument, ReviewAction } from '@/types/review'

export interface ReviewListParams {
  search?: string
  risk_level?: string
  review_status?: string
  page?: number
  page_size?: number
}

export function fetchReviewStats(): Promise<ReviewStats> {
  return fetchJSON<ReviewStats>(`${BASE_URL}/review-center/stats`)
}

export function fetchReviewDocuments(params: ReviewListParams = {}): Promise<ReviewListResponse> {
  const qs = new URLSearchParams()
  if (params.search) qs.set('search', params.search)
  if (params.risk_level) qs.set('risk_level', params.risk_level)
  if (params.review_status) qs.set('review_status', params.review_status)
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  const suffix = qs.toString() ? `?${qs.toString()}` : ''
  return fetchJSON<ReviewListResponse>(`${BASE_URL}/review-center/documents${suffix}`)
}

export function fetchReviewDetail(docId: string): Promise<ReviewDocument> {
  return fetchJSON<ReviewDocument>(`${BASE_URL}/review-center/documents/${docId}`)
}

export function submitReviewAction(
  docId: string,
  action: ReviewAction,
  comment: string,
  scenarioType?: string,
  approved?: boolean,
): Promise<ReviewDocument> {
  return fetchJSON<ReviewDocument>(
    `${BASE_URL}/review-center/documents/${docId}/review?action=${action}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        approved: approved ?? (action === 'approve'),
        review_comment: comment || null,
        scenario_type: scenarioType || null,
      }),
    },
  )
}
