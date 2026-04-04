import type { AuditResponse } from '../types/audit'

interface PageSummaryCardProps {
  data?: AuditResponse['page_data']
}

export default function PageSummaryCard({ data }: PageSummaryCardProps) {
  const displayData = data || {
    title: 'Example Domain - SEO Example',
    meta_description: 'This is a mock description for the SEO audit result.',
    headings: ['H1: Welcome to Example Domain', 'H2: About Our Services'],
    image_urls: ['https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=400&q=80'],
    author_found: true,
    date_found: true,
    social_links: []
  }

  const primaryImage = displayData.image_urls?.[0];

  return (
    <div className="edge-border bg-[#efece4] overflow-hidden">
      <div className="px-6 py-4 border-b border-zinc-400 flex items-center justify-between bg-zinc-800/5">
        <span className="typewriter text-xl uppercase tracking-tighter">Meta-Data Analysis</span>
        {primaryImage && (
          <span className="text-[10px] font-mono text-zinc-400 bg-zinc-800/5 px-2 py-0.5 border border-zinc-300">
            IMG_ID: {Math.random().toString(36).substring(7).toUpperCase()}
          </span>
        )}
      </div>
      <div className="p-8 space-y-8 relative">
        {/* Simple Image Asset */}
        {primaryImage && (
          <div className="hidden lg:block absolute top-8 right-8 w-48">
            <div className="aspect-square bg-white border border-zinc-300 shadow-sm overflow-hidden group flex items-center justify-center">
              <img
                src={primaryImage}
                alt="Subject Evidence"
                className="w-full h-full object-contain p-1"
              />
              <div className="absolute bottom-0 right-0 bg-zinc-800 text-white text-[8px] px-1 font-mono uppercase opacity-40">
                Primary Asset
              </div>
            </div>
          </div>
        )}

        <div className={`space-y-2 group ${primaryImage ? 'lg:pr-56' : ''}`}>
          <h4 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest border-l-2 border-zinc-300 pl-2">Page Title</h4>
          <p className="text-xl font-medium italic text-zinc-800 leading-tight">
            {displayData.title || <span className="opacity-30">[NO TITLE DATA]</span>}
          </p>
        </div>

        <div className={`space-y-2 group ${primaryImage ? 'lg:pr-56' : ''}`}>
          <h4 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest border-l-2 border-zinc-300 pl-2">Summary Description</h4>
          <div className="text-sm border border-zinc-300 p-4 bg-white/40 shadow-inner italic leading-relaxed text-zinc-700">
            {displayData.meta_description || "Subject contains no explicit meta-description for archival purposes."}
          </div>
        </div>

        {/* Mobile/Small Screen Image */}
        {primaryImage && (
          <div className="lg:hidden w-full aspect-video bg-white border border-zinc-300 flex items-center justify-center">
            <img src={primaryImage} className="w-full h-full object-contain p-2" />
          </div>
        )}

        {displayData.social_links && displayData.social_links.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest border-l-2 border-zinc-300 pl-2">Entity Linkage (Social)</h4>
            <div className="flex flex-wrap gap-2">
              {displayData.social_links.map((link, idx) => {
                const label = link.includes('linkedin') ? 'LINKEDIN' :
                  link.includes('twitter') || link.includes('x.com') ? 'X/TWITTER' :
                    link.includes('wikipedia') ? 'WIKIPEDIA' :
                      link.includes('wikidata') ? 'WIKIDATA' : 'LINK';
                return (
                  <a
                    key={idx}
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[10px] font-mono bg-zinc-800 text-parchment px-2 py-0.5 hover:bg-zinc-700 transition-colors"
                  >
                    [{label}]
                  </a>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
