import type { AuditResponse } from '../types/audit'
import PageSummaryCard from './PageSummaryCard.tsx'
import JsonLdViewer from './JsonLdViewer'

interface AuditResultProps {
  result?: AuditResponse | null
  loading?: boolean
}

export default function AuditResult({ result, loading }: AuditResultProps) {
  if (!result && !loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 edge-border bg-white/20 text-zinc-500">
        <svg className="w-16 h-16 mb-4 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <p className="typewriter text-lg uppercase tracking-widest font-bold">AWAITING TARGET</p>
        <p className="text-xs uppercase mt-2 tracking-tight opacity-60">SUBMIT A URL TO BEGIN STRUCTURAL ANALYSIS</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-6">
        <div className="stamp typewriter text-xl animate-pulse">Analyzing...</div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Left Column: Metadata & Structure */}
      <div className="md:col-span-2 space-y-8">
        {result && <PageSummaryCard data={result.page_data} />}
        
        <div className="edge-border p-6 bg-white/30">
          <h2 className="typewriter text-2xl border-b border-zinc-400 pb-2 mb-4 uppercase tracking-tighter">
            Structure: Heading Hierarchy
          </h2>
          <ul className="space-y-2 font-mono text-sm">
            {result?.page_data.headings.map((heading, i) => (
              <li key={i} className="flex gap-3 leading-tight border-b border-zinc-200 pb-1 last:border-0 hover:bg-zinc-100/50 transition-colors">
                <span className="opacity-50 shrink-0 select-none">[{String(i + 1).padStart(2, '0')}]</span>
                <span className="break-words">{heading}</span>
              </li>
            )) || <li className="opacity-40 italic">No headings detected in subject.</li>}
          </ul>
        </div>
      </div>

      {/* Right Column: Classification & Flags */}
      <div className="space-y-8">
        <div className="edge-border p-6 bg-zinc-100 text-center flex flex-col items-center justify-center min-h-[200px]">
          <h2 className="typewriter text-xl mb-4 uppercase opacity-60">Classification</h2>
          <div className="text-3xl font-bold border-4 border-ink p-4 inline-block mb-2 typewriter tracking-tighter bg-white shadow-[2px_2px_0px_var(--color-ink)]">
            {result?.detected_schema_type || 'UNKNOWN'}
          </div>
          <p className="text-[10px] uppercase font-bold tracking-widest mt-2">Detected Subject Category</p>
        </div>

        <div className="edge-border p-5 bg-ink text-parchment space-y-4">
          <h3 className="typewriter uppercase text-sm tracking-widest border-b border-zinc-600 pb-2">Technical Flags</h3>
          <div className="space-y-2">
            <TechnicalFlag label="Author Validated" value={result?.page_data.author_found} />
            <TechnicalFlag label="Chronology Found" value={result?.page_data.date_found} />
            <TechnicalFlag label="Social Footprint" value={(result?.page_data.social_links.length || 0) > 0} />
            <TechnicalFlag label="Canonical Match" value={!!result?.page_data.canonical_url} />
          </div>
        </div>
      </div>

      {/* Full Width Section: JSON-LD Viewer */}
      <div className="md:col-span-3 space-y-4">
        <h3 className="typewriter text-xl uppercase tracking-widest border-b-2 border-ink inline-block pb-1">
          Schema.org JSON-LD
        </h3>
        {result && <JsonLdViewer json={result.json_ld} />}
      </div>
    </div>
  )
}

function TechnicalFlag({ label, value }: { label: string, value: boolean | undefined }) {
  return (
    <div className="flex items-center justify-between text-xs font-mono uppercase tracking-tight">
      <span className="opacity-70">{label}</span>
      <span className={value ? "text-green-400 font-bold" : "text-amber-500 font-bold"}>
        [{value ? "YES" : "NO"}]
      </span>
    </div>
  )
}
