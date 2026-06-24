import { useState, useEffect, useCallback, useRef } from 'react'
import type { ProcessTask, TaskStats, TaskLog } from '@/types/processTask'
import { fetchTaskStats, fetchProcessTasks, fetchTaskDetail, fetchTaskLogs, submitTaskToReview } from '@/lib/api'

export function useProcessTasks() {
  // ── list ────────────────────────────────────────────────
  const [tasks, setTasks] = useState<ProcessTask[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // filters
  const [search, setSearch] = useState('')
  const [stageFilter, setStageFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  // ── stats ───────────────────────────────────────────────
  const [stats, setStats] = useState<TaskStats | null>(null)

  // ── detail panel ────────────────────────────────────────
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<ProcessTask | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [logs, setLogs] = useState<TaskLog[]>([])
  const [logsLoading, setLogsLoading] = useState(false)
  const [panelOpen, setPanelOpen] = useState(false)

  const abortRef = useRef<AbortController | null>(null)

  // ── load list ───────────────────────────────────────────
  const loadTasks = useCallback(
    (p?: number) => {
      const targetPage = p ?? page
      setLoading(true)
      setError(null)

      fetchProcessTasks({
        search: search || undefined,
        stage: stageFilter || undefined,
        status: statusFilter || undefined,
        page: targetPage,
        page_size: pageSize,
      })
        .then((res) => {
          setTasks(res.items)
          setTotal(res.total)
          setPage(res.page)
          setLoading(false)
        })
        .catch((err) => {
          setError(err.message)
          setLoading(false)
        })
    },
    [search, stageFilter, statusFilter, page, pageSize],
  )

  // ── load stats ──────────────────────────────────────────
  const loadStats = useCallback(() => {
    fetchTaskStats()
      .then(setStats)
      .catch(() => { /* stats are decorative, ignore errors */ })
  }, [])

  // ── load detail + logs ──────────────────────────────────
  const selectTask = useCallback(
    (id: string) => {
      setSelectedId(id)
      setPanelOpen(true)
      setDetailLoading(true)
      setLogsLoading(true)

      // cancel any in-flight
      if (abortRef.current) abortRef.current.abort()
      abortRef.current = new AbortController()

      fetchTaskDetail(id)
        .then((d) => {
          if (!abortRef.current?.signal.aborted) {
            setDetail(d)
            setDetailLoading(false)
          }
        })
        .catch(() => {
          if (!abortRef.current?.signal.aborted) setDetailLoading(false)
        })

      fetchTaskLogs(id)
        .then((l) => {
          if (!abortRef.current?.signal.aborted) {
            setLogs(l)
            setLogsLoading(false)
          }
        })
        .catch(() => {
          if (!abortRef.current?.signal.aborted) setLogsLoading(false)
        })
    },
    [],
  )

  const closePanel = useCallback(() => {
    setPanelOpen(false)
    setSelectedId(null)
    setDetail(null)
    setLogs([])
  }, [])

  // ── submit to review (manual gate) ─────────────────────
  const submitToReview = useCallback(async () => {
    if (!selectedId) return
    const updated = await submitTaskToReview(selectedId)
    setDetail(updated)
    await loadTasks()
    await loadStats()
  }, [selectedId, loadTasks, loadStats])

  // ── init ────────────────────────────────────────────────
  useEffect(() => {
    loadStats()
  }, [loadStats])

  useEffect(() => {
    loadTasks()
  }, [loadTasks])

  // cleanup
  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort()
    }
  }, [])

  return {
    // list
    tasks,
    total,
    page,
    pageSize,
    loading,
    error,
    // filters
    search,
    setSearch,
    stageFilter,
    setStageFilter,
    statusFilter,
    setStatusFilter,
    // stats
    stats,
    // detail
    selectedId,
    detail,
    detailLoading,
    logs,
    logsLoading,
    panelOpen,
    selectTask,
    closePanel,
    submitToReview,
    // actions
    loadTasks,
    setPage,
  }
}
