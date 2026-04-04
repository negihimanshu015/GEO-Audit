import { useState } from 'react'
import AuditForm from './components/AuditForm'
import AuditResult from './components/AuditResult'
import { runAudit } from './library/api'
import type { AuditResponse } from './types/audit'

function App() {
  const [result, setResult] = useState<AuditResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAudit = async (url: string) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await runAudit(url)
      setResult(data)
    } catch (err: any) {
      setError(err?.message || 'Something went wrong during the audit.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-4 md:p-8 relative">
      <div className="fixed inset-0 grid-bg pointer-events-none"></div>

      <main className="max-w-4xl mx-auto relative z-10">
        <header className="flex flex-col md:flex-row justify-between items-start mb-12 border-b-2 border-ink pb-6 gap-6">
          <div>
            <h1 className="text-5xl typewriter uppercase tracking-tighter mb-2">GEO-Audit</h1>
          </div>
          <div className="text-right self-end md:self-start min-h-[1.5rem]">
            {result && (
              <p className="text-xs font-bold uppercase animate-in fade-in duration-500">
                Timestamp: {new Date(result.audit_timestamp).toLocaleString()}
              </p>
            )}
          </div>
        </header>

        <section className="mb-16">
          <AuditForm onSubmit={handleAudit} loading={loading} />
          {error && (
            <div className="mt-4 p-4 border-2 border-red-800 bg-red-100 text-red-900 edge-border typewriter text-sm animate-in fade-in slide-in-from-top-2 duration-300">
              <strong>[ERROR]:</strong> {error}
            </div>
          )}
        </section>

        <section>
          <AuditResult result={result} loading={loading} />
        </section>

        {result && (
          <footer className="mt-16 edge-border p-8 bg-white/40 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <h2 className="typewriter text-2xl mb-6 uppercase tracking-tighter border-b-2 border-ink inline-block pb-1">
              GEO-Notes
            </h2>
            <div className="space-y-4 max-w-3xl">
              {/* Success Banner if no critical/warning notes */}
              {result.geo_notes.every(n => n.severity === 'info') && (
                <div className="mb-8 p-6 border-2 border-emerald-500/30 bg-emerald-500/5 edge-border flex items-center gap-4 animate-in zoom-in duration-500">
                  <span className="text-2xl text-emerald-600">✓</span>
                  <div>
                    <p className="typewriter text-lg font-bold text-emerald-800 tracking-wider">PAGE IS GEO-READY</p>
                    <p className="text-[10px] uppercase font-mono text-emerald-600 opacity-70">Structural verification successful</p>
                  </div>
                </div>
              )}

              {result.geo_notes.map((note, idx) => (
                <p
                  key={idx}
                  className={`p-4 border-l-4 italic text-sm animate-in fade-in slide-in-from-left-4 duration-500 shadow-sm ${note.severity === 'critical' ? 'border-red-600 bg-red-50 text-red-900' :
                    note.severity === 'warning' ? 'border-amber-500 bg-amber-50 text-amber-900' :
                      'border-emerald-500 bg-emerald-50/50 text-emerald-900'
                    }`}
                >
                  {note.severity === 'info' ? '✓ ' : '"'}
                  {note.message}
                  {note.severity !== 'info' && '"'}
                </p>
              ))}
            </div>
          </footer>
        )}
      </main>
    </div>
  )
}

export default App
