export interface DataSource {
  id: string; // instance specific id
  name: string
  mimeType: string | null
  filePath?: string
  connectionSettings?: Record<string, any>
}
