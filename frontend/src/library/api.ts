import type { AuditResponse } from '../types/audit'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Sends a POST request to the backend to start a website audit.
 * @param url The URL of the website to audit.
 */
export async function runAudit(url: string): Promise<AuditResponse> {
    const response = await fetch(`${API_BASE_URL}/audit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
    })

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Audit failed with status ${response.status}`)
    }

    return response.json()
}

export async function getHealth(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/health`)
    if (!response.ok) throw new Error('API health check failed')
    return response.json()
}
