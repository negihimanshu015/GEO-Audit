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

  const downloadJson = () => {
    const blob = new Blob([jsonString], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'schema.json'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="edge-border bg-white overflow-hidden relative group">
      {isAvailable && (
        <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
          <button
            onClick={copyToClipboard}
            className="px-3 py-1 bg-ink text-parchment text-[10px] typewriter uppercase tracking-widest hover:bg-zinc-700 transition-colors"
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
          <button
            onClick={downloadJson}
            className="px-3 py-1 bg-ink text-parchment text-[10px] typewriter uppercase tracking-widest hover:bg-zinc-700 transition-colors"
          >
            Download
          </button>
        </div>
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
