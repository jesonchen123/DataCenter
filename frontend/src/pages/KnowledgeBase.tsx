import { useKnowledgeBase } from '@/hooks/useKnowledgeBase'
import { DocumentList } from '@/components/knowledge/DocumentList'
import { DocumentDetail } from '@/components/knowledge/DocumentDetail'

export function KnowledgeBase() {
  const {
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
  } = useKnowledgeBase()

  return (
    <div className="flex flex-col h-full" style={{ minHeight: 600 }}>
      {/* Page Title */}
      <div className="mb-4">
        <h2
          className="font-bold"
          style={{ fontSize: 22, color: '#1a1a2e', letterSpacing: '-0.02em' }}
        >
          知识库
        </h2>
        <p style={{ fontSize: 13, color: '#999', marginTop: 2 }}>
          数据中台 · 知识文档 · 浏览与管理
          {stats && (
            <span style={{ marginLeft: 10 }}>
              共 <span style={{ color: '#0066CC', fontWeight: 500 }}>{stats.total}</span> 条
              {' · '}高质量 <span style={{ color: '#389e0d', fontWeight: 500 }}>{stats.high_quality}</span> 条
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
          scenarioFilter={scenarioFilter}
          riskFilter={riskFilter}
          statusFilter={statusFilter}
          onSearchChange={setSearch}
          onScenarioFilterChange={setScenarioFilter}
          onRiskFilterChange={setRiskFilter}
          onStatusFilterChange={setStatusFilter}
          onSelect={selectDoc}
        />

        {/* Right Panel: Document Detail */}
        <DocumentDetail
          detail={detail}
          loading={detailLoading}
          updating={updating}
          onUpdate={updateDoc}
          onSubmitReview={submitForReview}
        />
      </div>

      {/* Pagination */}
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
