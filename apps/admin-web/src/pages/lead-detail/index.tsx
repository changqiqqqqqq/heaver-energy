import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import FollowupDrawer from '../../components/FollowupDrawer'
import TransferSupplierModal from '../../components/TransferSupplierModal'
import { leadApi, type LeadDetail, type LeadSensitive } from '../../services/lead.api'
import { formatDateTime, formatEmpty, LEAD_STATUS_LABELS, NEED_TYPE_LABELS, PROFILE_LABELS } from '../../utils/format'

function JsonValue({ value }: { value: unknown }) {
  if (value === undefined || value === null || value === '') {
    return <span>-</span>
  }
  if (typeof value === 'object') {
    return <span>{JSON.stringify(value)}</span>
  }
  return <span>{String(value)}</span>
}

export default function LeadDetailPage() {
  const params = useParams()
  const navigate = useNavigate()
  const leadId = Number(params.id)
  const [lead, setLead] = useState<LeadDetail>()
  const [sensitive, setSensitive] = useState<LeadSensitive>()
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [followupOpen, setFollowupOpen] = useState(false)
  const [transferOpen, setTransferOpen] = useState(false)
  const [savingNote, setSavingNote] = useState(false)

  const serviceRequestId = useMemo(() => {
    const first = lead?.service_requests?.[0]
    return typeof first?.id === 'number' ? first.id : undefined
  }, [lead])

  const load = async () => {
    if (!leadId) {
      return
    }
    try {
      setLoading(true)
      setError('')
      const data = await leadApi.detail(leadId)
      setLead(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '线索详情加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [leadId])

  const revealSensitive = async () => {
    const data = await leadApi.sensitive(leadId)
    setSensitive(data)
  }

  const updateStatus = async (status: string) => {
    await leadApi.updateStatus(leadId, status, '后台详情页手动更新状态')
    await load()
  }

  const saveNote = async () => {
    if (!note.trim()) {
      return
    }
    try {
      setSavingNote(true)
      await leadApi.createNote(leadId, note.trim())
      setNote('')
      await load()
    } finally {
      setSavingNote(false)
    }
  }

  if (loading) {
    return <div className="loading">正在加载线索详情...</div>
  }

  if (error || !lead) {
    return <div className="error-box">{error || '线索不存在'}</div>
  }

  return (
    <div className="lead-detail-page page-grid">
      <div className="detail-hero card">
        <button className="ghost-button" type="button" onClick={() => navigate('/leads')}>返回列表</button>
        <div className="detail-title-block">
          <div className="detail-kicker">{lead.lead_no}</div>
          <h2>{formatEmpty(lead.enterprise_name) || '未填写企业'}</h2>
          <p>{lead.result_summary || '暂无测评摘要，建议先完成一次顾问跟进。'}</p>
        </div>
        <div className="detail-actions">
          <button className="primary-button" type="button" onClick={() => setFollowupOpen(true)}>新增跟进</button>
          <button className="ghost-button" type="button" onClick={() => setTransferOpen(true)}>转接供应商</button>
          <button className="ghost-button" type="button" onClick={revealSensitive}>查看敏感信息</button>
        </div>
      </div>

      <section className="detail-grid">
        <div className="card detail-panel">
          <div className="card-header">
            <div>
              <h2 className="card-title">基础信息</h2>
              <div className="card-subtitle">线索画像、来源和状态</div>
            </div>
          </div>
          <div className="detail-list">
            <div><span>状态</span><strong>{LEAD_STATUS_LABELS[lead.lead_status] || lead.lead_status}</strong></div>
            <div><span>等级</span><strong>{lead.lead_grade || '-'}</strong></div>
            <div><span>画像</span><strong>{lead.profile_code ? PROFILE_LABELS[lead.profile_code] || lead.profile_code : '-'}</strong></div>
            <div><span>需求</span><strong>{lead.primary_need_type ? NEED_TYPE_LABELS[lead.primary_need_type] || lead.primary_need_type : '-'}</strong></div>
            <div><span>来源</span><strong>{formatEmpty(lead.source_entry)}</strong></div>
            <div><span>最近活跃</span><strong>{formatDateTime(lead.last_activity_at)}</strong></div>
            <div><span>联系人</span><strong>{sensitive ? formatEmpty(sensitive.contact_name) : '点击查看'}</strong></div>
            <div><span>手机号</span><strong>{sensitive ? formatEmpty(sensitive.phone_masked) : lead.has_phone_authorized ? '已授权' : '未授权'}</strong></div>
          </div>
          <div className="status-actions">
            <button className="ghost-button" type="button" onClick={() => updateStatus('following')}>标记跟进中</button>
            <button className="ghost-button" type="button" onClick={() => updateStatus('transferred_supplier')}>标记已转接</button>
            <button className="danger-button" type="button" onClick={() => updateStatus('closed')}>关闭线索</button>
          </div>
        </div>

        <div className="card detail-panel">
          <div className="card-header">
            <div>
              <h2 className="card-title">测评结果</h2>
              <div className="card-subtitle">经营体质画像和维度分</div>
            </div>
          </div>
          <div className="record-list">
            {lead.submissions.length ? (
              lead.submissions.map((item) => (
                <div className="record-item" key={String(item.id)}>
                  <strong>{item.profile_code ? PROFILE_LABELS[String(item.profile_code)] || String(item.profile_code) : '测评记录'}</strong>
                  <span>总分：<JsonValue value={item.total_score} /></span>
                  <span>等级：<JsonValue value={item.lead_grade} /></span>
                  <small>{formatDateTime(String(item.created_at || ''))}</small>
                </div>
              ))
            ) : (
              <div className="empty compact-empty">暂无测评记录</div>
            )}
          </div>
        </div>
      </section>

      <section className="detail-grid detail-grid-wide">
        <div className="card detail-panel">
          <div className="card-header">
            <div>
              <h2 className="card-title">服务链路</h2>
              <div className="card-subtitle">初筛、服务需求、账单和供应商转接</div>
            </div>
          </div>
          <div className="timeline">
            {lead.screenings.map((item) => (
              <div className="timeline-item" key={`screening-${String(item.id)}`}>
                <span className="timeline-dot" />
                <strong>免费初筛：{formatEmpty(item.enterprise_name)}</strong>
                <p>{formatEmpty(item.region_text)} / {formatEmpty(item.enterprise_type)} / 状态 {formatEmpty(item.status)}</p>
              </div>
            ))}
            {lead.service_requests.map((item) => (
              <div className="timeline-item" key={`service-${String(item.id)}`}>
                <span className="timeline-dot" />
                <strong>服务需求：{item.primary_need_type ? NEED_TYPE_LABELS[String(item.primary_need_type)] || String(item.primary_need_type) : '-'}</strong>
                <p>{formatEmpty(item.description)}</p>
              </div>
            ))}
            {lead.bill_uploads.map((item) => (
              <div className="timeline-item" key={`bill-${String(item.id)}`}>
                <span className="timeline-dot" />
                <strong>账单上传：{formatEmpty(item.bill_month)}</strong>
                <p>解析状态：{formatEmpty(item.parse_status)}，文件 ID：{formatEmpty(item.file_id)}</p>
              </div>
            ))}
            {lead.transfers.map((item) => (
              <div className="timeline-item" key={`transfer-${String(item.id)}`}>
                <span className="timeline-dot" />
                <strong>供应商转接：供应商 #{formatEmpty(item.supplier_id)}</strong>
                <p>状态：{formatEmpty(item.transfer_status)}</p>
              </div>
            ))}
            {!lead.screenings.length && !lead.service_requests.length && !lead.bill_uploads.length && !lead.transfers.length ? (
              <div className="empty compact-empty">暂无服务链路记录</div>
            ) : null}
          </div>
        </div>

        <div className="card detail-panel">
          <div className="card-header">
            <div>
              <h2 className="card-title">跟进与备注</h2>
              <div className="card-subtitle">内部运营协作记录</div>
            </div>
          </div>
          <div className="timeline">
            {lead.followups.map((item) => (
              <div className="timeline-item" key={`followup-${String(item.id)}`}>
                <span className="timeline-dot" />
                <strong>跟进：{formatEmpty(item.followup_result)}</strong>
                <p>{formatEmpty(item.content)}</p>
              </div>
            ))}
            {lead.notes.map((item) => (
              <div className="timeline-item" key={`note-${String(item.id)}`}>
                <span className="timeline-dot" />
                <strong>备注</strong>
                <p>{formatEmpty(item.content)}</p>
              </div>
            ))}
          </div>
          <div className="note-box">
            <textarea className="textarea-field" value={note} onChange={(event) => setNote(event.target.value)} placeholder="新增内部备注..." />
            <button className="primary-button" type="button" disabled={savingNote} onClick={saveNote}>{savingNote ? '保存中...' : '保存备注'}</button>
          </div>
        </div>
      </section>

      <FollowupDrawer open={followupOpen} leadId={lead.id} onClose={() => setFollowupOpen(false)} onSaved={load} />
      <TransferSupplierModal open={transferOpen} leadId={lead.id} serviceRequestId={serviceRequestId} onClose={() => setTransferOpen(false)} onSaved={load} />
    </div>
  )
}

