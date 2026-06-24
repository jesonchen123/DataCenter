import { useReviewCenter } from '@/hooks/useReviewCenter'
import { DocumentList } from '@/components/review/DocumentList'
import { DocumentDetail } from '@/components/review/DocumentDetail'

export function ReviewCenter() {
  const {
    docs, total, page, pageSize, loading, error,
    search, setSearch,
    riskFilter, setRiskFilter,
    statusFilter, setStatusFilter,
    stats,
    selectedId, detail, detailLoading,
    selectDoc,
    submitting, submitReview,
    setPage,
  } = useReviewCenter()

  return (
    <div className="flex flex-col h-full" style={{ minHeight: 600 }}>
      {/* Page Title */}
      <div className="mb-4">
        <h2
          className="font-bold"
          style={{ fontSize: 22, color: '#1a1a2e', letterSpacing: '-0.02em' }}
        >
          审核中心
        </h2>
        <p style={{ fontSize: 13, color: '#999', marginTop: 2 }}>
          数据中台 · 文档审核 · 合规确认
          {stats && (
            <span style={{ marginLeft: 10 }}>
              待审 <span style={{ color: '#d48806', fontWeight: 500 }}>{stats.total}</span> 条
              {' · '}需修改 <span style={{ color: '#cf1322', fontWeight: 500 }}>{stats.need_edit}</span> 条
            </span>
          )}
        </p>
      </div>

      {/* Two Column Layout */}
      <div className="flex flex-1 rounded-xl shadow-sm border border-gray-100 overflow-hidden" style={{ minHeight: 0 }}>
        {/* Left Panel: Document List */}
        <DocumentList
          docs={docs}
          total={total}
          loading={loading}
          error={error}
          selectedId={selectedId}
          search={search}
          riskFilter={riskFilter}
          statusFilter={statusFilter}
          onSearchChange={setSearch}
          onRiskFilterChange={setRiskFilter}
          onStatusFilterChange={setStatusFilter}
          onSelect={selectDoc}
        />

        {/* Right Panel: Document Detail */}
        <DocumentDetail
          detail={detail}
          loading={detailLoading}
          submitting={submitting}
          onSubmitReview={submitReview}
        />
      </div>

      {/* Simple pagination for left panel */}
      {total > pageSize && (
        <div className="flex items-center justify-between mt-3 px-2">
          <span style={{ fontSize: 12, color: '#888' }}>
            共 {total} 条
          </span>
          <div className="flex items-center gap-1">
            {Array.from({ length: Math.min(Math.ceil(total / pageSize), 5) }, (_, i) => {
              const totalPages = Math.ceil(total / pageSize)
              let pn: number
              if (totalPages <= 5) {
                pn = i + 1
              } else if (page <= 3) {
                pn = i + 1
              } else if (page >= totalPages - 2) {
                pn = totalPages - 4 + i
              } else {
                pn = page - 2 + i
              }
              return (
                <button
                  key={pn}
                  className="rounded-md px-2.5 py-1 text-xs border cursor-pointer"
                  style={{
                    background: pn === page ? '#0066CC' : 'transparent',
                    color: pn === page ? '#fff' : '#555',
                    borderColor: pn === page ? '#0066CC' : '#e0e0e0',
                  }}
                  onClick={() => setPage(pn)}
                >
                  {pn}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
