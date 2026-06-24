import { useState, useEffect, useCallback } from 'react'
import type { ReviewDocument, ReviewStats, ReviewAction } from '@/types/review'
import {
  fetchReviewStats,
  fetchReviewDocuments,
  fetchReviewDetail,
  submitReviewAction,
} from '@/lib/api'

export function useReviewCenter() {
  const [docs, setDocs] = useState<ReviewDocument[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const pageSize = 20
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const [stats, setStats] = useState<ReviewStats | null>(null)

  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<ReviewDocument | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const loadDocs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetchReviewDocuments({
        search,
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
  }, [search, riskFilter, statusFilter, page])

  const loadStats = useCallback(async () => {
    try {
      const s = await fetchReviewStats()
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
  }, [search, riskFilter, statusFilter])

  const selectDoc = useCallback(async (id: string) => {
    if (id === selectedId) return
    setSelectedId(id)
    setDetailLoading(true)
    try {
      const d = await fetchReviewDetail(id)
      setDetail(d)
    } catch {
      setDetail(null)
    } finally {
      setDetailLoading(false)
    }
  }, [selectedId])

  const closeDetail = useCallback(() => {
    setSelectedId(null)
    setDetail(null)
  }, [])

  const submitReview = useCallback(async (action: ReviewAction, comment: string, scenarioType?: string) => {
    if (!selectedId) return
    setSubmitting(true)
    try {
      const updated = await submitReviewAction(selectedId, action, comment, scenarioType)
      setDetail(updated)
      // Reload list and stats
      await loadDocs()
      await loadStats()
    } catch (err: unknown) {
      throw err
    } finally {
      setSubmitting(false)
    }
  }, [selectedId, loadDocs, loadStats])

  return {
    docs, total, page, pageSize, loading, error,
    search, setSearch,
    riskFilter, setRiskFilter,
    statusFilter, setStatusFilter,
    stats,
    selectedId, detail, detailLoading,
    selectDoc, closeDetail,
    submitting, submitReview,
    setPage,
  }
}
