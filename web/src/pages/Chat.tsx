import { useState, type ChangeEvent } from 'react'
import { FileText, Loader2 } from 'lucide-react'
import { api } from '../api/client'
import { useUser } from '../auth/AuthContext'
import { ChatPanel } from '../components/ChatPanel'
import { errorMessage } from '../components/Toast'
import { Notice } from '../components/ui'

type UploadState =
  | { kind: 'idle' }
  | { kind: 'uploading'; name: string }
  | { kind: 'done'; name: string }
  | { kind: 'error'; message: string }

export function Chat() {
  const { userId } = useUser()
  const [upload, setUpload] = useState<UploadState>({ kind: 'idle' })

  async function handleFile(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return

    setUpload({ kind: 'uploading', name: file.name })
    try {
      await api.uploadDocument(userId, file)
      setUpload({ kind: 'done', name: file.name })
    } catch (err) {
      setUpload({ kind: 'error', message: errorMessage(err) })
    }
  }

  return (
    <>
      <div className="card upload" style={{ maxWidth: 768, width: '100%', margin: '0 auto 16px' }}>
        <label className="field">
          <span className="row">
            <FileText className="icon" size={18} aria-hidden="true" />
            Upload a health document (PDF or TXT) to personalize AI answers
          </span>
          <input type="file" accept=".pdf,.txt" onChange={handleFile} disabled={upload.kind === 'uploading'} />
        </label>
        <p className="caption">Uploaded documents are stored privately and used only to answer your questions.</p>
        {upload.kind === 'uploading' && (
          <p className="caption row" role="status">
            <Loader2 className="icon spin" size={14} aria-hidden="true" />
            Processing {upload.name}...
          </p>
        )}
        {upload.kind === 'done' && <Notice tone="success">'{upload.name}' added to your knowledge base!</Notice>}
        {upload.kind === 'error' && <Notice tone="error">Upload failed: {upload.message}</Notice>}
      </div>
      <ChatPanel />
    </>
  )
}
