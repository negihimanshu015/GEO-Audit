import type { AuditResponse } from '../types/audit'

interface PageSummaryCardProps {
  data?: AuditResponse['page_data']
}

export default function PageSummaryCard({ data }: PageSummaryCardProps) {
  // Use mock data if no real data is provided
  const displayData = data || {
    title: 'Example Domain - SEO Example',
    meta_description: 'This is a mock description for the SEO audit result.',
    headings: ['H1: Welcome to Example Domain', 'H2: About Our Services'],
    image_urls: [],
    author_found: true,
    date_found: true,
    social_links: []
  }

  return (
    <div className="edge-border bg-[#efece4] overflow-hidden">
      <div className="px-6 py-4 border-b border-zinc-400 flex items-center justify-between bg-zinc-800/5">
        <span className="typewriter text-xl uppercase tracking-tighter">Subject: Meta-Data Analysis</span>
      </div>
      <div className="p-8 space-y-8">
        <div className="space-y-2 group">
          <h4 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest border-l-2 border-zinc-300 pl-2">Page Title</h4>
          <p className="text-xl font-medium italic text-zinc-800 leading-tight">
            {displayData.title || <span className="opacity-30">[NO TITLE DATA]</span>}
          </p>
        </div>

        <div className="space-y-2 group">
          <h4 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest border-l-2 border-zinc-300 pl-2">Summary Description</h4>
          <div className="text-sm border border-zinc-300 p-4 bg-white/40 shadow-inner italic leading-relaxed text-zinc-700">
            {displayData.meta_description || "Subject contains no explicit meta-description for archival purposes."}
          </div>
        </div>

        {displayData.canonical_url && (
          <div className="pt-4 border-t border-zinc-300/50 flex items-center gap-2 text-[10px] font-mono opacity-60">
            <span className="font-bold uppercase shrink-0">Origin Node:</span>
            <span className="truncate">{displayData.canonical_url}</span>
          </div>
        )}
      </div>
    </div>
  )
}
