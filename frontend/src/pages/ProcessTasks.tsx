import { useProcessTasks } from '@/hooks/useProcessTasks'
import { StatsRow } from '@/components/process/StatsRow'
import { TaskTable } from '@/components/process/TaskTable'
import { TaskDetail } from '@/components/process/TaskDetail'

export function ProcessTasks() {
  const {
    tasks, total, page, pageSize, loading, error,
    search, setSearch,
    stageFilter, setStageFilter,
    statusFilter, setStatusFilter,
    stats,
    selectedId, detail, detailLoading,
    logs, logsLoading, panelOpen,
    selectTask, closePanel,
    submitToReview,
    setPage,
  } = useProcessTasks()

  return (
    <>
      {/* Page Title */}
      <div className="mb-6">
        <h2
          className="font-bold"
          style={{ fontSize: 22, color: '#1a1a2e', letterSpacing: '-0.02em' }}
        >
          处理任务
        </h2>
        <p style={{ fontSize: 13, color: '#999', marginTop: 2 }}>
          数据中台 · 任务队列 · LLM 处理状态追踪
        </p>
      </div>

      {/* Stats Row */}
      <StatsRow stats={stats} />

      {/* Two Column: table + detail panel */}
      <div className="flex gap-0" style={{ minHeight: 600 }}>
        {/* Table area — flex-1 when panel closed, shrinks when open */}
        <div className="flex-1 min-w-0">
          <TaskTable
            tasks={tasks}
            total={total}
            page={page}
            pageSize={pageSize}
            loading={loading}
            error={error}
            selectedId={selectedId}
            search={search}
            stageFilter={stageFilter}
            statusFilter={statusFilter}
            onSearchChange={setSearch}
            onStageFilterChange={setStageFilter}
            onStatusFilterChange={setStatusFilter}
            onSelect={selectTask}
            onPageChange={setPage}
          />
        </div>

        {/* Detail Panel — slides in from right */}
        <TaskDetail
          detail={detail}
          loading={detailLoading}
          logs={logs}
          logsLoading={logsLoading}
          open={panelOpen}
          onClose={closePanel}
          onSubmitToReview={submitToReview}
        />
      </div>
    </>
  )
}
