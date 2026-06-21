import { useEffect, useState } from 'react'

import { supplierApi, type Supplier } from '../../services/supplier.api'

type TransferSupplierModalProps = {
  open: boolean
  leadId?: number
  serviceRequestId?: number
  onClose: () => void
  onSaved: () => void
}

export default function TransferSupplierModal({ open, leadId, serviceRequestId, onClose, onSaved }: TransferSupplierModalProps) {
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [supplierId, setSupplierId] = useState('')
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (open) {
      supplierApi.list().then(setSuppliers)
    }
  }, [open])

  if (!open) {
    return null
  }

  const submit = async () => {
    if (!leadId || !supplierId) {
      return
    }
    try {
      setSaving(true)
      await supplierApi.transfer({
        lead_id: leadId,
        supplier_id: Number(supplierId),
        service_request_id: serviceRequestId,
        transfer_reason: reason.trim() || undefined,
      })
      onSaved()
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-mask">
      <div className="modal-panel">
        <div className="drawer-header">
          <div>
            <h3>转接供应商</h3>
            <p>将当前线索转给合适的能源服务商</p>
          </div>
          <button className="ghost-button" type="button" onClick={onClose}>关闭</button>
        </div>
        <div className="drawer-body">
          <label className="form-row">
            <span className="form-label">供应商</span>
            <select className="select-field" value={supplierId} onChange={(event) => setSupplierId(event.target.value)}>
              <option value="">请选择供应商</option>
              {suppliers.map((supplier) => (
                <option value={supplier.id} key={supplier.id}>{supplier.name}</option>
              ))}
            </select>
          </label>
          <label className="form-row">
            <span className="form-label">转接说明</span>
            <textarea className="textarea-field" value={reason} onChange={(event) => setReason(event.target.value)} placeholder="填写转接原因、用户诉求或注意事项" />
          </label>
        </div>
        <div className="drawer-footer">
          <button className="primary-button" type="button" disabled={saving} onClick={submit}>{saving ? '转接中...' : '确认转接'}</button>
        </div>
      </div>
    </div>
  )
}

