import { useState, useEffect, useCallback } from 'react'
import type { KnowledgeDocument, KnowledgeStats } from '@/types/knowledge'
import {
  fetchKnowledgeStats,
  fetchKnowledgeDocuments,
  fetchKnowledgeDetail,
  updateKnowledgeDocument,
  submitKnowledgeForReview,
} from '@/lib/api'

export function useKnowledgeBase() {
  const [docs, setDocs] = useState<KnowledgeDocument[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const pageSize = 20
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [scenarioFilter, setScenarioFilter] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const [stats, setStats] = useState<KnowledgeStats | null>(null)

  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<KnowledgeDocument | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [updating, setUpdating] = useState(false)

  const loadDocs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetchKnowledgeDocuments({
        search,
        scenario_type: scenarioFilter,
        risk_level: riskFilter,
        review_status: statusFilter,
        page,
        page_size: pageSize,
      })
      setDocs(res.items)
      setTotal(res.total)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }, [search, scenarioFilter, riskFilter, statusFilter, page])

  const loadStats = useCallback(async () => {
    try {
      const s = await fetchKnowledgeStats()
      setStats(s)
    } catch {
      // stats are non-critical
    }
  }, [])

  useEffect(() => {
    loadStats()
  }, [loadStats])

  useEffect(() => {
    loadDocs()
  }, [loadDocs])

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1)
  }, [search, scenarioFilter, riskFilter, statusFilter])

  const selectDoc = useCallback(async (id: string) => {
    if (id === selectedId) return
    setSelectedId(id)
    setDetailLoading(true)
    try {
      const d = await fetchKnowledgeDetail(id)
      setDetail(d)
    } catch {
      setDetail(null)
    } finally {
      setDetailLoading(false)
    }
  }, [selectedId])

  const updateDoc = useCallback(async (payload: Record<string, unknown>) => {
    if (!selectedId) return
    setUpdating(true)
    try {
      const updated = await updateKnowledgeDocument(selectedId, payload)
      setDetail(updated)
      await loadDocs()
    } finally {
      setUpdating(false)
    }
  }, [selectedId, loadDocs])

  const submitForReview = useCallback(async () => {
    if (!selectedId) return
    setUpdating(true)
    try {
      const updated = await submitKnowledgeForReview(selectedId)
      setDetail(updated)
      await loadDocs()
      await loadStats()
    } finally {
      setUpdating(false)
    }
  }, [selectedId, loadDocs, loadStats])

  return {
    docs, total, page, pageSize, loading, error,
    search, setSearch,
    scenarioFilter, setScenarioFilter,
    riskFilter, setRiskFilter,
    statusFilter, setStatusFilter,
    stats,
    selectedId, detail, detailLoading,
    selectDoc,
    updating, updateDoc, submitForReview,
    setPage,
  }
}
