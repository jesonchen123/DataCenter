export interface ReviewStats {
  total: number
  pending_review: number
  need_edit: number
  approved: number
  rejected: number
}

export interface ReviewDocument {
  id: string
  doc_no: string
  title: string
  content: string
  question_examples: string[] | null
  tags: string[] | null
  scenario_type: string | null
  risk_level: 'low' | 'medium' | 'high'
  quality_score: number
  review_status: 'pending_review' | 'need_edit' | 'approved' | 'rejected' | 'archived'
  review_comment: string | null
  reviewer_id: string | null
  reviewer_name: string | null
  reviewed_at: string | null
  submitter_name: string
  created_at: string
  updated_at: string
}

export interface ReviewListResponse {
  items: ReviewDocument[]
  total: number
  page: number
  page_size: number
}

export type ReviewAction = 'approve' | 'reject' | 'request_changes' | 'save_note'
