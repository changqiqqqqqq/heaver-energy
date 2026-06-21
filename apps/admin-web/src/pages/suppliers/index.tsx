import { FormEvent, useEffect, useState } from 'react'

import { supplierApi, type Supplier } from '../../services/supplier.api'
import { formatEmpty } from '../../utils/format'

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    name: '',
    supplier_type: '售电服务商',
    region_scope: '',
    service_tags: '',
    contact_name: '',
    contact_phone_masked: '',
    remark: '',
  })

  const load = async () => {
    try {
      setLoading(true)
      setError('')
      setSuppliers(await supplierApi.list())
    } catch (err) {
      setError(err instanceof Error ? err.message : '供应商加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!form.name.trim()) {
      return
    }
    await supplierApi.create({
      name: form.name.trim(),
      supplier_type: form.supplier_type.trim(),
      region_scope: form.region_scope.split(/[，,]/).map((item) => item.trim()).filter(Boolean),
      service_tags: form.service_tags.split(/[，,]/).map((item) => item.trim()).filter(Boolean),
      contact_name: form.contact_name.trim() || undefined,
      contact_phone_masked: form.contact_phone_masked.trim() || undefined,
      remark: form.remark.trim() || undefined,
    })
    setForm({ name: '', supplier_type: '售电服务商', region_scope: '', service_tags: '', contact_name: '', contact_phone_masked: '', remark: '' })
    await load()
  }

  return (
    <div className="suppliers-page page-grid">
      <section className="card supplier-form-card">
        <div className="card-header">
          <div>
            <h2 className="card-title">新增供应商</h2>
            <div className="card-subtitle">维护可承接线索的能源服务商</div>
          </div>
        </div>
        <form className="supplier-form" onSubmit={submit}>
          <label className="form-row">
            <span className="form-label">供应商名称</span>
            <input className="field" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          </label>
          <label className="form-row">
            <span className="form-label">类型</span>
            <input className="field" value={form.supplier_type} onChange={(event) => setForm({ ...form, supplier_type: event.target.value })} />
          </label>
          <label className="form-row">
            <span className="form-label">服务区域</span>
            <input className="field" placeholder="广东, 浙江" value={form.region_scope} onChange={(event) => setForm({ ...form, region_scope: event.target.value })} />
          </label>
          <label className="form-row">
            <span className="form-label">服务标签</span>
            <input className="field" placeholder="售电, 光伏, 储能" value={form.service_tags} onChange={(event) => setForm({ ...form, service_tags: event.target.value })} />
          </label>
          <label className="form-row">
            <span className="form-label">联系人</span>
            <input className="field" value={form.contact_name} onChange={(event) => setForm({ ...form, contact_name: event.target.value })} />
          </label>
          <label className="form-row">
            <span className="form-label">联系电话</span>
            <input className="field" value={form.contact_phone_masked} onChange={(event) => setForm({ ...form, contact_phone_masked: event.target.value })} />
          </label>
          <label className="form-row supplier-remark">
            <span className="form-label">备注</span>
            <input className="field" value={form.remark} onChange={(event) => setForm({ ...form, remark: event.target.value })} />
          </label>
          <button className="primary-button" type="submit">保存供应商</button>
        </form>
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">供应商列表</h2>
            <div className="card-subtitle">共 {suppliers.length} 家供应商</div>
          </div>
        </div>
        {loading ? <div className="loading">正在加载供应商...</div> : null}
        {error ? <div className="error-box">{error}</div> : null}
        {!loading && !error ? (
          <table className="table">
            <thead>
              <tr>
                <th>名称</th>
                <th>类型</th>
                <th>区域</th>
                <th>标签</th>
                <th>联系人</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {suppliers.map((supplier) => (
                <tr key={supplier.id}>
                  <td><strong>{supplier.name}</strong><div className="muted-text">{formatEmpty(supplier.remark)}</div></td>
                  <td>{supplier.supplier_type}</td>
                  <td>{supplier.region_scope_json?.join('、') || '-'}</td>
                  <td>{supplier.service_tags_json?.join('、') || '-'}</td>
                  <td>{formatEmpty(supplier.contact_name)} / {formatEmpty(supplier.contact_phone_masked)}</td>
                  <td><span className="tag tag-green">{supplier.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </section>
    </div>
  )
}

