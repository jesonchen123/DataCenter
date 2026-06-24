import { useRef, type DragEvent, type ChangeEvent } from 'react'
import { CloudUpload, Plus } from 'lucide-react'

interface DropZoneProps {
  uploading: boolean
  onUpload: (formData: FormData) => void
}

export function DropZone({ uploading, onUpload }: DropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  function handleFile(file: File) {
    const fd = new FormData()
    fd.append('file', file)
    onUpload(fd)
  }

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
    if (inputRef.current) inputRef.current.value = ''
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault()
    const f = e.dataTransfer.files?.[0]
    if (f) handleFile(f)
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault()
  }

  return (
    <div
      className="drop-zone flex flex-col items-center justify-center py-10 px-8 cursor-pointer"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onClick={() => inputRef.current?.click()}
    >
      <div
        className="flex items-center justify-center rounded-full mb-4"
        style={{ width: 72, height: 72, background: 'rgba(0,102,204,0.06)' }}
      >
        <CloudUpload size={36} color="#0066CC" />
      </div>
      <p className="font-semibold mb-2" style={{ fontSize: 18, color: '#1a1a2e' }}>
        拖拽文档到此处或点击选择
      </p>
      <p style={{ fontSize: 13, color: '#999', marginBottom: 20 }}>
        支持 PDF、Word、Excel、PPT、TXT · 单个文件不超过 10MB
      </p>
      <button
        className="flex items-center gap-2 px-6 py-3 rounded-lg text-white font-medium transition-all hover:shadow-md disabled:opacity-60"
        style={{ background: '#0066CC', fontSize: 14 }}
        disabled={uploading}
        onClick={(e) => {
          e.stopPropagation()
          inputRef.current?.click()
        }}
      >
        <Plus size={16} />
        {uploading ? '上传中...' : '选择文件'}
      </button>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept=".pdf,.docx,.txt,.json,.xlsx,.pptx"
        onChange={handleChange}
      />
    </div>
  )
}
