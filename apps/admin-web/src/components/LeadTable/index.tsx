import type { LeadListItem } from '../../services/lead.api'
import { formatDateTime, formatEmpty, LEAD_STATUS_LABELS, NEED_TYPE_LABELS, PROFILE_LABELS } from '../../utils/format'

type LeadTableProps = {
  items: LeadListItem[]
  onOpen: (lead: LeadListItem) => void
}

export default function LeadTable({ items, onOpen }: LeadTableProps) {
  return (
    <table className="table lead-table">
      <thead>
        <tr>
          <th>线索</th>
          <th>企业</th>
          <th>画像</th>
          <th>等级</th>
          <th>需求</th>
          <th>状态</th>
          <th>数据</th>
          <th>最近活跃</th>
        </tr>
      </thead>
      <tbody>
        {items.map((lead) => (
          <tr className="table-row-clickable" key={lead.id} onClick={() => onOpen(lead)}>
            <td>
              <strong>{lead.lead_no}</strong>
              <div className="muted-text">{formatEmpty(lead.source_entry)}</div>
            </td>
            <td>{formatEmpty(lead.enterprise_name)}</td>
            <td>{lead.profile_code ? PROFILE_LABELS[lead.profile_code] || lead.profile_code : '-'}</td>
            <td><span className="tag">{lead.lead_grade || '-'}</span></td>
            <td>{lead.primary_need_type ? NEED_TYPE_LABELS[lead.primary_need_type] || lead.primary_need_type : '-'}</td>
            <td><span className="tag tag-blue">{LEAD_STATUS_LABELS[lead.lead_status] || lead.lead_status}</span></td>
            <td>
              <div className="lead-flags">
                <span className={lead.has_bill_uploaded ? 'flag flag-on' : 'flag'}>账单</span>
                <span className={lead.has_phone_authorized ? 'flag flag-on' : 'flag'}>手机号</span>
              </div>
            </td>
            <td>{formatDateTime(lead.last_activity_at || lead.created_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

