export interface PageData {
  title: string
  meta_description?: string
  headings: string[]
  image_urls: string[]
  canonical_url?: string
  author_found: boolean
  date_found: boolean
  social_links: string[]
}

export interface GeoNote {
  message: string
  severity: 'warning' | 'critical' | 'info'
}

export interface AuditResponse {
  url: string
  page_data: PageData
  detected_schema_type: string
  json_ld: Record<string, any>
  geo_notes: GeoNote[]
  audit_timestamp: string
}
