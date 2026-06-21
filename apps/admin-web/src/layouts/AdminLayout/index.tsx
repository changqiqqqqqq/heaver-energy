import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'

import { authApi } from '../../services/auth.api'
import { clearAdminSession, getCachedAdmin, hasAdminToken, type AdminUser } from '../../store/auth.store'

type NavItem = {
  path: string
  label: string
  icon: string
  badge?: string
  disabled?: boolean
}

const navGroups: Array<{ title: string; items: NavItem[] }> = [
  {
    title: '数据概览',
    items: [
      { path: '/', label: '今日数据', icon: '▮' },
      { path: '/analytics/trends', label: '趋势分析', icon: '⌁', disabled: true },
      { path: '/analytics/funnel', label: '转化漏斗', icon: '▾', disabled: true },
    ],
  },
  {
    title: '用户管理',
    items: [
      { path: '/users', label: '用户列表', icon: '♙', disabled: true },
      { path: '/questionnaire-submissions', label: '测评记录', icon: '▤', disabled: true },
      { path: '/leads', label: '线索管理', icon: '☆' },
    ],
  },
  {
    title: '消息中心',
    items: [
      { path: '/messages', label: '用户消息', icon: '□', badge: '12', disabled: true },
      { path: '/notifications', label: '系统通知', icon: '♢', disabled: true },
    ],
  },
  {
    title: '系统',
    items: [
      { path: '/suppliers', label: '供应商管理', icon: '◎' },
      { path: '/settings', label: '系统设置', icon: '⚙' },
    ],
  },
]

const titles: Array<[RegExp, string]> = [
  [/^\/$/, '今日数据概览'],
  [/^\/leads\/\d+/, '线索详情'],
  [/^\/leads/, '线索管理'],
  [/^\/suppliers/, '供应商管理'],
  [/^\/settings/, '系统设置'],
]

export default function AdminLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const [admin, setAdmin] = useState<AdminUser | undefined>(() => getCachedAdmin())

  const pageTitle = useMemo(() => {
    return titles.find(([pattern]) => pattern.test(location.pathname))?.[1] || '运营数据后台'
  }, [location.pathname])

  useEffect(() => {
    if (!hasAdminToken()) {
      navigate('/login', { replace: true })
      return
    }
    authApi.me().then(setAdmin).catch(() => navigate('/login', { replace: true }))
  }, [navigate])

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      clearAdminSession()
      navigate('/login', { replace: true })
    }
  }

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="brand-panel">
          <div className="brand-logo">⌁</div>
          <div>
            <div className="brand-title">河狸数字能源</div>
            <div className="brand-subtitle">运营数据后台</div>
          </div>
        </div>

        <nav className="side-nav">
          {navGroups.map((group) => (
            <div className="side-group" key={group.title}>
              <div className="side-group-title">{group.title}</div>
              {group.items.map((item) =>
                item.disabled ? (
                  <div className="side-link side-link-disabled" key={item.path}>
                    <span className="side-icon">{item.icon}</span>
                    <span>{item.label}</span>
                    {item.badge ? <span className="side-badge">{item.badge}</span> : null}
                  </div>
                ) : (
                  <NavLink className={({ isActive }) => (isActive ? 'side-link side-link-active' : 'side-link')} to={item.path} key={item.path}>
                    <span className="side-icon">{item.icon}</span>
                    <span>{item.label}</span>
                    {item.badge ? <span className="side-badge">{item.badge}</span> : null}
                  </NavLink>
                ),
              )}
            </div>
          ))}
        </nav>
      </aside>

      <section className="admin-main">
        <header className="admin-topbar">
          <h1>{pageTitle}</h1>
          <div className="topbar-actions">
            <button className="date-button" type="button">▣ 2026年6月21日（今天）⌄</button>
            <button className="export-button" type="button">⇩ 导出报表</button>
            <button className="admin-button" type="button" onClick={logout}>{admin?.display_name || '管理员'}</button>
          </div>
        </header>
        <main className="admin-content">
          <Outlet />
        </main>
      </section>
    </div>
  )
}

