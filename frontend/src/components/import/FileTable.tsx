import type { ImportFile } from '@/types/import'
import {
  FileText,
  FileSpreadsheet,
  File,
  Eye,
  Trash2,
  Send,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  ExternalLink,
} from 'lucide-react'

function getFileIcon(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  if (ext === 'xlsx' || ext === 'xls') return FileSpreadsheet
  if (ext === 'pdf' || ext === 'docx' || ext === 'doc' || ext === 'txt') return FileText
  return File
}

function getFileColor(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  if (ext === 'pdf') return '#ff6b6b'
  if (ext === 'docx' || ext === 'doc') return '#4dabf7'
  if (ext === 'xlsx' || ext === 'xls') return '#51cf66'
  return '#adb5bd'
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function getProcessStatusBadge(status: string | null | undefined): {
  label: string
  color: string
  bg: string
  border: string
  icon: JSX.Element
} {
  if (!status) {
    return {
      label: '未提交',
      color: '#999',
      bg: '#fafafa',
      border: '#e8e8e8',
      icon: <Clock size={12} />,
    }
  }
  switch (status) {
    case 'success':
    case 'completed':
      return {
        label: '处理完成',
        color: '#389e0d',
        bg: '#f6ffed',
        border: '#b7eb8f',
        icon: <CheckCircle size={12} />,
      }
    case 'processing':
    case 'running':
      return {
        label: '处理中',
        color: '#0066CC',
        bg: '#e6f4ff',
        border: '#91caff',
        icon: <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' } as React.CSSProperties} />,
      }
    case 'pending':
      return {
        label: '待处理',
        color: '#d48806',
        bg: '#fff7e6',
        border: '#ffd591',
        icon: <Clock size={12} />,
      }
    case 'failed':
      return {
        label: '处理失败',
        color: '#cf1322',
        bg: '#fff1f0',
        border: '#ffa39e',
        icon: <XCircle size={12} />,
      }
    default:
      return {
        label: status,
        color: '#999',
        bg: '#fafafa',
        border: '#e8e8e8',
        icon: <Clock size={12} />,
      }
  }
}

interface FileTableProps {
  files: ImportFile[]
  selectedId: string | null
  onSelect: (id: string) => void
  onDelete: (id: string) => void
  onProcess: (mockChatId: string) => void
  processing: boolean
}

export function FileTable({ files, selectedId, onSelect, onDelete, onProcess, processing }: FileTableProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex-1 flex flex-col">
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <h3 className="font-semibold" style={{ fontSize: 15, color: '#1a1a2e' }}>
          已上传文件
        </h3>
        <span style={{ fontSize: 12, color: '#999' }}>共 {files.length} 个文件</span>
      </div>
      <div className="overflow-x-auto flex-1">
        <table className="w-full">
          <thead>
            <tr>
              <th style={{ width: '28%' }}>文件名</th>
              <th style={{ width: '12%' }}>文件大小</th>
              <th style={{ width: '14%' }}>上传时间</th>
              <th style={{ width: '16%' }}>处理状态</th>
              <th style={{ width: '16%' }}>解析状态</th>
              <th style={{ width: '14%' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {files.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center text-gray-400 py-12">
                  暂无上传文件，拖拽文件到上方区域开始上传
                </td>
              </tr>
            ) : (
              files.map((file) => {
                const Icon = getFileIcon(file.original_filename)
                const iconColor = getFileColor(file.original_filename)
                const isSelected = selectedId === file.mock_chat_id
                const processBadge = getProcessStatusBadge(file.process_status)

                return (
                  <tr
                    key={file.id}
                    onClick={() => onSelect(file.mock_chat_id)}
                    style={{ cursor: 'pointer', background: isSelected ? '#f5f8ff' : undefined }}
                  >
                    <td>
                      <div className="flex items-center gap-3">
                        <Icon size={20} color={iconColor} />
                        <span style={{ fontWeight: 500, fontSize: 13 }}>
                          {file.original_filename}
                        </span>
                      </div>
                    </td>
                    <td style={{ fontSize: 12, color: '#666' }}>{formatSize(file.file_size)}</td>
                    <td style={{ fontSize: 12, color: '#666' }}>
                      {new Date(file.created_at).toLocaleString('zh-CN', {
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td>
                      <span
                        className="status-badge"
                        style={{
                          background: processBadge.bg,
                          color: processBadge.color,
                          border: `1px solid ${processBadge.border}`,
                        }}
                      >
                        {processBadge.icon}
                        <span style={{ marginLeft: 4 }}>{processBadge.label}</span>
                      </span>
                    </td>
                    <td>
                      {file.import_status === 'completed' ? (
                        <span
                          className="status-badge"
                          style={{ background: '#f6ffed', color: '#389e0d', border: '1px solid #b7eb8f' }}
                        >
                          <CheckCircle size={12} style={{ marginRight: 4 }} />
                          已完成
                        </span>
                      ) : file.import_status === 'failed' ? (
                        <div className="flex items-center gap-2">
                          <span
                            className="status-badge"
                            style={{ background: '#fff1f0', color: '#cf1322', border: '1px solid #ffa39e' }}
                          >
                            <XCircle size={12} style={{ marginRight: 4 }} />
                            失败
                          </span>
                          {file.error_message && (
                            <span style={{ fontSize: 11, color: '#ff4d4f' }}>{file.error_message}</span>
                          )}
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <div className="progress-bar" style={{ width: 80 }}>
                            <div
                              className="progress-fill"
                              style={{ width: '45%', background: '#faad14' }}
                            />
                          </div>
                          <span
                            className="status-badge"
                            style={{ background: '#fff7e6', color: '#d48806', border: '1px solid #ffd591' }}
                          >
                            <span
                              style={{
                                width: 5,
                                height: 5,
                                borderRadius: '50%',
                                background: '#faad14',
                                marginRight: 5,
                                display: 'inline-block',
                                animation: 'pulse 1.5s infinite',
                              }}
                            />
                            解析中
                          </span>
                        </div>
                      )}
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <button
                          className="action-btn preview"
                          onClick={(e) => {
                            e.stopPropagation()
                            onSelect(file.mock_chat_id)
                          }}
                        >
                          <Eye size={13} />
                          预览
                        </button>
                        {!file.process_task_id ? (
                          <button
                            className="action-btn"
                            style={{ color: '#0066CC' }}
                            onClick={(e) => {
                              e.stopPropagation()
                              onProcess(file.mock_chat_id)
                            }}
                            disabled={processing}
                          >
                            <Send size={13} />
                            提交任务
                          </button>
                        ) : file.process_status === 'success' || file.process_status === 'completed' ? (
                          <a
                            className="action-btn"
                            style={{ color: '#389e0d' }}
                            href={`/tasks?search=${file.process_task_id}`}
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink size={13} />
                            查看结果
                          </a>
                        ) : (
                          <a
                            className="action-btn"
                            style={{ color: '#0066CC' }}
                            href={`/tasks?search=${file.process_task_id}`}
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink size={13} />
                            查看进度
                          </a>
                        )}
                        <button
                          className="action-btn delete"
                          onClick={(e) => {
                            e.stopPropagation()
                            onDelete(file.mock_chat_id)
                          }}
                        >
                          <Trash2 size={13} />
                          删除
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
