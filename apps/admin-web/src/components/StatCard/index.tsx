import { formatNumber, formatPercent } from '../../utils/format'

type StatCardProps = {
  label: string
  value: number
  changeRate?: number
  icon?: string
  tone?: 'orange' | 'blue' | 'green' | 'purple'
}

export default function StatCard({ label, value, changeRate = 0, icon = '◎', tone = 'orange' }: StatCardProps) {
  const isDown = changeRate < 0

  return (
    <div className={`stat-card stat-card-${tone}`}>
      <div className="stat-icon">{icon}</div>
      <div className={isDown ? 'stat-change stat-change-down' : 'stat-change'}>
        {isDown ? '↓' : '↑'} {formatPercent(Math.abs(changeRate))}
      </div>
      <div className="stat-value">{formatNumber(value)}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

