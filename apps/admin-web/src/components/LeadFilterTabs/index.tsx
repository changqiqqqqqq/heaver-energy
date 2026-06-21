import { LEAD_STATUS_LABELS } from '../../utils/format'

type LeadFilterTabsProps = {
  value: string
  onChange: (value: string) => void
}

const tabs = [
  { value: '', label: '全部线索' },
  { value: 'pending_followup', label: LEAD_STATUS_LABELS.pending_followup },
  { value: 'following', label: LEAD_STATUS_LABELS.following },
  { value: 'transferred_supplier', label: LEAD_STATUS_LABELS.transferred_supplier },
  { value: 'closed', label: LEAD_STATUS_LABELS.closed },
]

export default function LeadFilterTabs({ value, onChange }: LeadFilterTabsProps) {
  return (
    <div className="lead-tabs">
      {tabs.map((tab) => (
        <button className={tab.value === value ? 'lead-tab lead-tab-active' : 'lead-tab'} type="button" key={tab.value} onClick={() => onChange(tab.value)}>
          {tab.label}
        </button>
      ))}
    </div>
  )
}

