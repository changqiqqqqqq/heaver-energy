import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { authApi } from '../../services/auth.api'

export default function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    try {
      setLoading(true)
      setError('')
      await authApi.login(username, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={submit}>
        <div className="login-logo">⌁</div>
        <h1>河狸数字能源</h1>
        <p>运营数据后台</p>
        <label className="form-row">
          <span className="form-label">账号</span>
          <input className="field" value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label className="form-row">
          <span className="form-label">密码</span>
          <input className="field" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error ? <div className="login-error">{error}</div> : null}
        <button className="primary-button login-submit" type="submit" disabled={loading}>{loading ? '登录中...' : '登录后台'}</button>
      </form>
    </main>
  )
}

