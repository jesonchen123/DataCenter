export interface ImportFile {
  id: string
  mock_chat_id: string
  source_platform: string
  business_line: string | null
  product_name: string | null
  scenario_type: string | null
  original_filename: string
  file_size: number
  category: string
  priority: string
  import_status: 'completed' | 'parsing' | 'failed'
  error_message: string | null
  message_count: number
  process_task_id: string | null
  process_status: string | null
  created_at: string
  updated_at: string
}

export interface PreviewMessage {
  message_id: string
  sender_role: 'customer' | 'staff' | 'system' | 'unknown'
  sender_name: string
  content: string
}

export interface ParsePreview {
  mock_chat_id: string
  filename: string
  import_status: string
  normalizer: string
  source_platform: string | null
  business_line: string | null
  product_name: string | null
  messages: PreviewMessage[]
  message_count: number
  customer_count: number
  staff_count: number
}

export interface UploadResult {
  mock_chat_id: string
  original_filename: string
  file_size: number
  category: string
  priority: string
  import_status: string
  normalizer: string | null
}
