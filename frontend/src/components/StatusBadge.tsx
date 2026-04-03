interface StatusBadgeProps {
  status: 'idle' | 'loading' | 'success' | 'error'
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const configs = {
    idle: {
      text: 'READY',
      className: 'border-zinc-400 text-zinc-400 rotate-0'
    },
    loading: {
      text: 'ANALYZING',
      className: 'border-stamp-red text-stamp-red animate-pulse'
    },
    success: {
      text: 'AUDIT COMPLETE',
      className: 'border-emerald-700 text-emerald-700 rotate-3'
    },
    error: {
      text: 'AUDIT FAILED',
      className: 'border-stamp-red text-stamp-red -rotate-6'
    }
  }

  const { text, className } = configs[status]

  return (
    <div className={`stamp text-[10px] ${className} transition-all duration-300`}>
      {text}
    </div>
  )
}
