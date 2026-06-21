import { API_BASE_URL } from '../../services/http'

export default function SettingsPage() {
  return (
    <div className="settings-page page-grid">
      <section className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">系统设置</h2>
            <div className="card-subtitle">当前后台运行配置和后续能力开关</div>
          </div>
        </div>
        <div className="settings-list">
          <div><span>API 地址</span><strong>{API_BASE_URL}</strong></div>
          <div><span>访问埋点</span><strong>未接入，当前看板使用链路数据兜底</strong></div>
          <div><span>消息系统</span><strong>MVP 阶段映射待跟进线索</strong></div>
          <div><span>权限模型</span><strong>当前启用管理员登录校验</strong></div>
        </div>
      </section>
    </div>
  )
}

