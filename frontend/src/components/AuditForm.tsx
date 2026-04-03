import { useState } from 'react'

interface AuditFormProps {
  onSubmit: (url: string) => void
  loading: boolean
}

export default function AuditForm({ onSubmit, loading }: AuditFormProps) {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) {
      onSubmit(url.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="edge-border bg-white/40 p-8">
      <div className="space-y-4">
        <label htmlFor="url-input" className="block typewriter text-lg mb-2 uppercase tracking-wide">
          Input URL :
        </label>
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            id="url-input"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/archive"
            required
            disabled={loading}
            className="flex-1 bg-transparent border-b-2 border-ink py-2 focus:outline-none placeholder:text-zinc-400 font-mono text-lg disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !url}
            className="bg-ink text-parchment px-10 py-3 typewriter uppercase hover:bg-zinc-700 transition-colors disabled:bg-zinc-400 disabled:cursor-not-allowed flex items-center justify-center min-w-[160px]"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing
              </span>
            ) : (
              'Audit'
            )}
          </button>
        </div>
      </div>
    </form>
  )
}
