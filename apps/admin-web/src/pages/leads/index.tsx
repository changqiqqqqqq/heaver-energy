import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import LeadFilterTabs from '../../components/LeadFilterTabs'
import LeadTable from '../../components/LeadTable'
import { leadApi, type LeadListItem, type LeadQuery, type PageResult } from '../../services/lead.api'

const defaultQuery: LeadQuery = {
  page: 1,
  page_size: 20,
  lead_status: '',
  lead_grade: '',
  profile_code: '',
  primary_need_type: '',
  has_bill_uploaded: '',
  has_phone_authorized: '',
}

export default function LeadsPage() {
  const navigate = useNavigate()
  const [query, setQuery] = useState<LeadQuery>(defaultQuery)
  const [page, setPage] = useState<PageResult<LeadListItem>>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async (nextQuery = query) => {
    try {
      setLoading(true)
      setError('')
      const data = await leadApi.list(nextQuery)
      setPage(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '线索加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const updateQuery = (patch: Partial<LeadQuery>) => {
    const nextQuery = { ...query, ...patch, page: patch.page || 1 }
    setQuery(nextQuery)
    load(nextQuery)
  }

  return (
    <div className="leads-page page-grid">
      <div className="card filter-card">
        <div className="card-header">
          <div>
            <h2 className="card-title">线索管理</h2>
            <div className="card-subtitle">按状态、画像、等级和业务动作筛选待跟进线索</div>
          </div>
          <button className="ghost-button" type="button" onClick={() => updateQuery(defaultQuery)}>重置筛选</button>
        </div>
        <div className="filter-body">
          <LeadFilterTabs value={query.lead_status || ''} onChange={(value) => updateQuery({ lead_status: value })} />
          <div className="filter-grid">
            <select className="select-field" value={query.lead_grade || ''} onChange={(event) => updateQuery({ lead_grade: event.target.value })}>
              <option value="">全部等级</option>
              <option value="A">A 级</option>
              <option value="B">B 级</option>
              <option value="C">C 级</option>
              <option value="D">D 级</option>
            </select>
            <select className="select-field" value={query.profile_code || ''} onChange={(event) => updateQuery({ profile_code: event.target.value })}>
              <option value="">全部画像</option>
              <option value="cost_sensitive">成本敏感型</option>
              <option value="growth_expansion">增长扩张型</option>
              <option value="stable_operation">稳健经营型</option>
              <option value="hidden_waste">隐性浪费型</option>
              <option value="energy_awakened">能源觉醒型</option>
              <option value="supplier_confused">供应商迷茫型</option>
            </select>
            <select className="select-field" value={query.primary_need_type || ''} onChange={(event) => updateQuery({ primary_need_type: event.target.value })}>
              <option value="">全部需求</option>
              <option value="energy_consulting">商电成本核查</option>
              <option value="quote_review">报价方案判断</option>
              <option value="supplier_recommendation">供应商推荐</option>
              <option value="solar_storage">光储方案</option>
            </select>
            <select
              className="select-field"
              value={query.has_bill_uploaded === '' ? '' : String(query.has_bill_uploaded)}
              onChange={(event) => updateQuery({ has_bill_uploaded: event.target.value === '' ? '' : event.target.value === 'true' })}
            >
              <option value="">账单不限</option>
              <option value="true">已上传账单</option>
              <option value="false">未上传账单</option>
            </select>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">线索列表</h2>
            <div className="card-subtitle">共 {page?.total || 0} 条线索</div>
          </div>
        </div>
        {loading ? <div className="loading">正在加载线索...</div> : null}
        {error ? <div className="error-box">{error}</div> : null}
        {!loading && !error && page ? (
          page.items.length ? (
            <>
              <LeadTable items={page.items} onOpen={(lead) => navigate(`/leads/${lead.id}`)} />
              <div className="pagination-bar">
                <button className="ghost-button" type="button" disabled={(query.page || 1) <= 1} onClick={() => updateQuery({ page: Math.max(1, (query.page || 1) - 1) })}>上一页</button>
                <span>第 {page.page} 页 / 共 {Math.max(1, Math.ceil(page.total / page.page_size))} 页</span>
                <button
                  className="ghost-button"
                  type="button"
                  disabled={page.page >= Math.ceil(page.total / page.page_size)}
                  onClick={() => updateQuery({ page: (query.page || 1) + 1 })}
                >
                  下一页
                </button>
              </div>
            </>
          ) : (
            <div className="empty">没有符合条件的线索</div>
          )
        ) : null}
      </div>
    </div>
  )
}

