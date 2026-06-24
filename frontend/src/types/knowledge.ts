export interface KnowledgeStats {
  total: number
  high_quality: number
  by_scenario: Record<string, number>
  by_risk: Record<string, number>
  by_status: Record<string, number>
}

export interface AuditEntry {
  id: string
  user_id: string | null
  username: string
  action: string
  detail: Record<string, unknown> | null
  created_at: string | null
}

export interface KnowledgeDocument {
  id: string
  doc_no: string
  title: string
  content: string
  question_examples: string[] | null
  tags: string[] | null
  scenario_type: string | null
  business_line: string | null
  product_name: string | null
  risk_level: 'low' | 'medium' | 'high'
  quality_score: number
  review_status: 'pending_review' | 'need_edit' | 'approved' | 'rejected' | 'archived'
  review_comment: string | null
  reviewer_id: string | null
  reviewer_name: string | null
  reviewed_at: string | null
  submitter_name: string
  price_filtered: boolean
  contains_price_intent: boolean
  contains_original_price: boolean
  is_desensitized: boolean
  created_by: string | null
  updated_by: string | null
  created_at: string
  updated_at: string
  audit_logs?: AuditEntry[]
}

export interface KnowledgeListResponse {
  items: KnowledgeDocument[]
  total: number
  page: number
  page_size: number
}
