import { useState, useEffect, useCallback } from 'react'
import type { ImportFile, ParsePreview } from '@/types/import'
import {
  fetchImportFiles,
  fetchParsePreview,
  uploadDocument as uploadDocumentApi,
  deleteImportFile as deleteImportFileApi,
  triggerProcessTask as triggerProcessTaskApi,
} from '@/lib/api'

export function useDocImport() {
  const [files, setFiles] = useState<ImportFile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [preview, setPreview] = useState<ParsePreview | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  const loadFiles = useCallback(async () => {
    try {
      setError(null)
      const data = await fetchImportFiles()
      setFiles(data)
      // Auto-select first file
      if (data.length > 0 && !selectedId) {
        setSelectedId(data[0].mock_chat_id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }, [selectedId])

  // Load preview when selectedId changes
  useEffect(() => {
    if (!selectedId) {
      setPreview(null)
      return
    }
    let cancelled = false
    setPreviewLoading(true)
    fetchParsePreview(selectedId)
      .then((data) => {
        if (!cancelled) setPreview(data)
      })
      .catch(() => {
        if (!cancelled) setPreview(null)
      })
      .finally(() => {
        if (!cancelled) setPreviewLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [selectedId])

  useEffect(() => {
    loadFiles()
  }, [loadFiles])

  const uploadDocument = useCallback(async (formData: FormData): Promise<boolean> => {
    setUploading(true)
    try {
      await uploadDocumentApi(formData)
      await loadFiles()
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败')
      return false
    } finally {
      setUploading(false)
    }
  }, [loadFiles])

  const deleteFile = useCallback(async (mockChatId: string) => {
    try {
      await deleteImportFileApi(mockChatId)
      if (selectedId === mockChatId) {
        setSelectedId(null)
        setPreview(null)
      }
      await loadFiles()
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败')
    }
  }, [loadFiles, selectedId])

  const selectFile = useCallback((mockChatId: string) => {
    setSelectedId(mockChatId)
  }, [])

  const processDocument = useCallback(async (mockChatId: string): Promise<boolean> => {
    try {
      setError(null)
      await triggerProcessTaskApi(mockChatId)
      await loadFiles()
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交任务失败')
      return false
    }
  }, [loadFiles])

  return {
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
    reload: loadFiles,
  }
}
