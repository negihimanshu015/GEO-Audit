import { useState } from 'react'

interface JsonLdViewerProps {
  json: object
}

export default function JsonLdViewer({ json }: JsonLdViewerProps) {
  const [copied, setCopied] = useState(false)
  const isAvailable = Object.keys(json).length > 0
  const jsonString = JSON.stringify(json, null, 2)

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(jsonString)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  return (
    <div className="edge-border bg-white overflow-hidden relative group">
      {isAvailable && (
        <button
          onClick={copyToClipboard}
          className="absolute top-2 right-2 px-3 py-1 bg-ink text-parchment text-[10px] typewriter uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity hover:bg-zinc-700 z-10"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      )}
      
      {isAvailable ? (
        <pre className="p-6 text-xs font-mono text-ink overflow-x-auto leading-relaxed scrollbar-thin scrollbar-thumb-zinc-400 scrollbar-track-transparent">
          <code>{jsonString}</code>
        </pre>
      ) : (
        <div className="p-12 text-center text-zinc-400 bg-zinc-50 italic text-sm">
          [NULL DATA] - No JSON-LD schema objects detected in the subject's source.
        </div>
      )}
    </div>
  )
}
