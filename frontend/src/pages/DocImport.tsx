import { useState, useCallback } from 'react'
import { useDocImport } from '@/hooks/useDocImport'
import { DropZone } from '@/components/import/DropZone'
import { FileTable } from '@/components/import/FileTable'
import { ImportConfig } from '@/components/import/ImportConfig'
import { ParsePreview } from '@/components/import/ParsePreview'

export function DocImport() {
  const {
    files,
    loading,
    error,
    selectedId,
    preview,
    previewLoading,
    uploading,
    uploadDocument,
    deleteFile,
    selectFile,
    processDocument,
  } = useDocImport()

  const [submitting, setSubmitting] = useState(false)

  // Config state (UI only for now)
  const [category, setCategory] = useState('金融报告')
  const [priority, setPriority] = useState('中')
  const [smartSplit, setSmartSplit] = useState(true)
  const [autoMetadata, setAutoMetadata] = useState(true)

  const handleUpload = useCallback(
    (formData: FormData) => {
      formData.append('category', category)
      formData.append('priority', priority)
      uploadDocument(formData)
    },
    [uploadDocument, category, priority],
  )

  const handleReset = useCallback(() => {
    setCategory('金融报告')
    setPriority('中')
    setSmartSplit(true)
    setAutoMetadata(true)
  }, [])

  const handleProcess = useCallback(
    async (mockChatId: string) => {
      setSubmitting(true)
      await processDocument(mockChatId)
      setSubmitting(false)
    },
    [processDocument],
  )

  return (
    <>
      {/* Page Title */}
      <div className="mb-6">
        <h2
          className="font-bold"
          style={{ fontSize: 22, color: '#1a1a2e', letterSpacing: '-0.02em' }}
        >
          文档导入
        </h2>
        <p style={{ fontSize: 13, color: '#999', marginTop: 2 }}>
          上传文档、配置元数据、预览解析结果
        </p>
      </div>

      {error && (
        <div
          className="mb-6 p-4 rounded-lg text-[13px]"
          style={{ background: '#fff1f0', color: '#cf1322', border: '1px solid #ffa39e' }}
        >
          {error}
        </div>
      )}

      {/* Two Column Layout */}
      <div className="flex gap-6" style={{ minHeight: 680 }}>
        {/* LEFT COLUMN (60%) */}
        <div className="flex-1 flex flex-col gap-5" style={{ minWidth: 0 }}>
          {/* Drop Zone */}
          <DropZone uploading={uploading} onUpload={handleUpload} />

          {/* File List Table */}
          <FileTable
            files={files}
            selectedId={selectedId}
            onSelect={selectFile}
            onDelete={deleteFile}
            onProcess={handleProcess}
            processing={submitting}
          />
        </div>

        {/* RIGHT COLUMN (40%) */}
        <div className="flex flex-col gap-5" style={{ width: 380, flexShrink: 0 }}>
          {/* Import Config Panel */}
          <ImportConfig
            category={category}
            priority={priority}
            smartSplit={smartSplit}
            autoMetadata={autoMetadata}
            onCategoryChange={setCategory}
            onPriorityChange={setPriority}
            onSmartSplitChange={setSmartSplit}
            onAutoMetadataChange={setAutoMetadata}
            onApply={() => {
              // Re-apply config - config is passed during upload
            }}
            onReset={handleReset}
          />

          {/* Parse Preview Panel */}
          <ParsePreview preview={preview} loading={previewLoading || loading} />
        </div>
      </div>
    </>
  )
}
