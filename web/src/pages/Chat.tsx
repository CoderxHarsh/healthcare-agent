import { useState, type ChangeEvent } from 'react'
import { api } from '../api/client'
import { useUser } from '../auth/AuthContext'
import { ChatPanel } from '../components/ChatPanel'
import { errorMessage } from '../components/Toast'

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
      <div className="card upload">
        <label className="field">
          📄 Upload Health Document (PDF/TXT) to personalize AI answers
          <input type="file" accept=".pdf,.txt" onChange={handleFile} disabled={upload.kind === 'uploading'} />
        </label>
        {upload.kind === 'uploading' && <p className="caption">📚 Processing {upload.name}...</p>}
        {upload.kind === 'done' && (
          <p className="notice notice-success">✅ '{upload.name}' added to your knowledge base!</p>
        )}
        {upload.kind === 'error' && <p className="notice notice-error">❌ Upload failed: {upload.message}</p>}
      </div>
      <ChatPanel />
    </>
  )
}
