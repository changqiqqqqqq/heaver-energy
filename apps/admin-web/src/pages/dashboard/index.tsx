import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import StatCard from '../../components/StatCard'
import { statisticsApi, type DashboardOverview, type DashboardTrendItem } from '../../services/statistics.api'
import { formatNumber, formatPercent } from '../../utils/format'

const cardMeta: Record<string, { icon: string; tone: 'orange' | 'blue' | 'green' | 'purple' }> = {
  visits: { icon: '◎', tone: 'orange' },
  submissions: { icon: '▤', tone: 'blue' },
  reports: { icon: '▭', tone: 'green' },
  consultations: { icon: '♙', tone: 'purple' },
}

const profileColors = ['#f47b00', '#3f6fd9', '#219653', '#f5b342', '#8a5cf6', '#13a9b8']

function TrendChart({ data }: { data: DashboardTrendItem[] }) {
  const width = 860
  const height = 330
  const padding = 44
  const maxValue = Math.max(10, ...data.flatMap((item) => [item.visits, item.submissions, item.reports]))

  const points = (key: 'visits' | 'submissions' | 'reports') => {
    return data
      .map((item, index) => {
        const x = padding + (index * (width - padding * 2)) / Math.max(1, data.length - 1)
        const y = height - padding - (item[key] / maxValue) * (height - padding * 2)
        return `${x},${y}`
      })
      .join(' ')
  }

  return (
    <div className="trend-chart">
      <div className="chart-legend">
        <span><i className="legend-dot legend-orange" />点击</span>
        <span><i className="legend-dot legend-blue" />答题</span>
        <span><i className="legend-dot legend-green" />领取</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="近7日核心数据趋势">
        {[0, 1, 2, 3].map((line) => {
          const y = padding + (line * (height - padding * 2)) / 3
          return <line x1={padding} x2={width - padding} y1={y} y2={y} stroke="#eee6de" strokeWidth="1" key={line} />
        })}
        <polyline points={points('visits')} fill="none" stroke="#ff7a00" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={points('submissions')} fill="none" stroke="#4774d8" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={points('reports')} fill="none" stroke="#23864e" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {data.map((item, index) => {
          const x = padding + (index * (width - padding * 2)) / Math.max(1, data.length - 1)
          return (
            <text x={x} y={height - 13} textAnchor="middle" fill="#9d948d" fontSize="12" key={item.date}>
              {item.date.slice(5).replace('-', '/')}
            </text>
          )
        })}
      </svg>
    </div>
  )
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const [overview, setOverview] = useState<DashboardOverview>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        setError('')
        const data = await statisticsApi.getOverview()
        setOverview(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : '看板加载失败')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const donutStyle = useMemo(() => {
    if (!overview?.profile_distribution.length) {
      return { background: '#f2eee9' }
    }
    let cursor = 0
    const segments = overview.profile_distribution.map((item, index) => {
      const start = cursor
      cursor += item.ratio
      return `${profileColors[index % profileColors.length]} ${start}% ${cursor}%`
    })
    return { background: `conic-gradient(${segments.join(', ')})` }
  }, [overview])

  if (loading) {
    return <div className="loading">正在加载今日运营数据...</div>
  }

  if (error || !overview) {
    return <div className="error-box">{error || '看板数据为空'}</div>
  }

  return (
    <div className="dashboard-page page-grid">
      <section className="stat-grid">
        {overview.cards.map((card) => (
          <StatCard
            key={card.key}
            label={card.label}
            value={card.value}
            changeRate={card.change_rate}
            icon={cardMeta[card.key]?.icon}
            tone={cardMeta[card.key]?.tone}
          />
        ))}
      </section>

      <section className="dashboard-main-grid">
        <div className="card trend-card">
          <div className="card-header">
            <div>
              <h2 className="card-title">近7日核心数据趋势</h2>
              <div className="card-subtitle">每日点击 / 答题 / 报告领取</div>
            </div>
          </div>
          <TrendChart data={overview.trend} />
        </div>

        <div className="card funnel-card">
          <div className="card-header">
            <div>
              <h2 className="card-title">今日转化漏斗</h2>
              <div className="card-subtitle">用户行为路径</div>
            </div>
          </div>
          <div className="funnel-list">
            {overview.funnel.map((step, index) => {
              const firstValue = overview.funnel[0]?.value || 1
              return (
                <div className="funnel-row" key={step.key}>
                  <div className="funnel-row-head">
                    <span>{step.label}</span>
                    <strong>{formatNumber(step.value)}</strong>
                  </div>
                  <div className="funnel-track">
                    <div className={`funnel-fill funnel-fill-${index}`} style={{ width: `${Math.min(100, (step.value / firstValue) * 100)}%` }} />
                  </div>
                  {index > 0 ? <div className="funnel-rate">↓ {formatPercent(step.conversion_rate)} 继续</div> : null}
                </div>
              )
            })}
          </div>
        </div>
      </section>

      <section className="dashboard-bottom-grid">
        <div className="card profile-card">
          <div className="card-header">
            <div>
              <h2 className="card-title">今日测评结果分布</h2>
              <div className="card-subtitle">{formatNumber(overview.cards.find((item) => item.key === 'submissions')?.value || 0)} 人完成测评</div>
            </div>
            <div className="donut" style={donutStyle} />
          </div>
          <table className="table profile-table">
            <thead>
              <tr>
                <th>体质类型</th>
                <th>人数</th>
                <th>占比</th>
                <th>预约率</th>
              </tr>
            </thead>
            <tbody>
              {overview.profile_distribution.length ? (
                overview.profile_distribution.map((item, index) => (
                  <tr key={item.profile_code}>
                    <td><span className={`profile-pill profile-pill-${index % 4}`}>{item.profile_name}</span></td>
                    <td>{formatNumber(item.count)}</td>
                    <td>{formatPercent(item.ratio)}</td>
                    <td className={item.consultation_rate >= 12 ? 'rate-hot' : ''}>{formatPercent(item.consultation_rate)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4}>暂无测评分布数据</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="card pending-card">
          <div className="card-header pending-header">
            <div>
              <h2 className="card-title">消息中心 · 待回复</h2>
              <div className="card-subtitle">后台消息管理</div>
            </div>
            <div className="pending-actions">
              <span className="pending-unread">{overview.pending_messages.length} 条未读</span>
              <button className="ghost-button" type="button">全部已读</button>
            </div>
          </div>
          <div className="pending-list">
            {overview.pending_messages.length ? (
              overview.pending_messages.map((message) => (
                <div className="pending-item" key={message.lead_id} onClick={() => navigate(`/leads/${message.lead_id}`)}>
                  <div className="pending-avatar">♙</div>
                  <div className="pending-copy">
                    <div className="pending-title">
                      {message.display_name}
                      {message.profile_name ? <span> · {message.profile_name}</span> : null}
                    </div>
                    <div className="pending-content">{message.content}</div>
                  </div>
                  <div className="pending-meta">
                    <span className="tag">待回复</span>
                    <small>{message.minutes_ago || 0}分钟前</small>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty">暂无待回复消息</div>
            )}
          </div>
          <div className="quick-reply-bar">
            <button className="ghost-button" type="button">快捷回复⌄</button>
            <input className="field" placeholder="输入回复内容..." disabled />
            <button className="primary-button" type="button">发送</button>
          </div>
        </div>
      </section>
    </div>
  )
}

