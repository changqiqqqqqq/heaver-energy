import { useState } from 'react'

import { leadApi } from '../../services/lead.api'

type FollowupDrawerProps = {
  open: boolean
  leadId?: number
  onClose: () => void
  onSaved: () => void
}

export default function FollowupDrawer({ open, leadId, onClose, onSaved }: FollowupDrawerProps) {
  const [content, setContent] = useState('')
  const [followupType, setFollowupType] = useState('phone')
  const [followupResult, setFollowupResult] = useState('contacted')
  const [saving, setSaving] = useState(false)

  if (!open) {
    return null
  }

  const submit = async () => {
    if (!leadId || !content.trim()) {
      return
    }
    try {
      setSaving(true)
      await leadApi.createFollowup({
        lead_id: leadId,
        followup_type: followupType,
        followup_result: followupResult,
        content: content.trim(),
      })
      setContent('')
      onSaved()
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="drawer-mask">
      <aside className="drawer-panel">
        <div className="drawer-header">
          <div>
            <h3>新增跟进</h3>
            <p>记录顾问与用户的沟通结果</p>
          </div>
          <button className="ghost-button" type="button" onClick={onClose}>关闭</button>
        </div>
        <div className="drawer-body">
          <label className="form-row">
            <span className="form-label">跟进方式</span>
            <select className="select-field" value={followupType} onChange={(event) => setFollowupType(event.target.value)}>
              <option value="phone">电话</option>
              <option value="wechat">微信</option>
              <option value="community">社群</option>
              <option value="offline">线下</option>
            </select>
          </label>
          <label className="form-row">
            <span className="form-label">跟进结果</span>
            <select className="select-field" value={followupResult} onChange={(event) => setFollowupResult(event.target.value)}>
              <option value="contacted">已联系</option>
              <option value="no_answer">未接通</option>
              <option value="interested">有兴趣</option>
              <option value="not_interested">暂不考虑</option>
              <option value="invalid">无效线索</option>
            </select>
          </label>
          <label className="form-row">
            <span className="form-label">跟进内容</span>
            <textarea className="textarea-field" value={content} onChange={(event) => setContent(event.target.value)} placeholder="填写沟通结论、下一步动作或用户关注点" />
          </label>
        </div>
        <div className="drawer-footer">
          <button className="primary-button" type="button" disabled={saving} onClick={submit}>{saving ? '保存中...' : '保存跟进'}</button>
        </div>
      </aside>
    </div>
  )
}

