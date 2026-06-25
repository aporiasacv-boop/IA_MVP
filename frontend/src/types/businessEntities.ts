export interface BusinessEntityItem {
  entity_id: number
  entity_code: string
  entity_name: string
  source_system: string
  source_table: string
  source_column: string
  movement_count: number
  movement_amount: string
  first_seen: string | null
  last_seen: string | null
  classification_status: string
  confidence: string | null
  created_at: string
  updated_at: string
}

export interface BusinessEntityListResponse {
  items: BusinessEntityItem[]
  total: number
  page: number
  page_size: number
}

export interface BusinessEntityStatistics {
  business_entities_total: number
  business_entities_loaded: number
  duplicated_entities: number
  last_entity_refresh: string | null
  by_source_column: Record<string, number>
  by_classification_status: Record<string, number>
}

export type EntitySortField =
  | 'entity_code'
  | 'entity_name'
  | 'movement_count'
  | 'movement_amount'
  | 'first_seen'
  | 'last_seen'
  | 'updated_at'

export interface EntityListParams {
  search?: string
  source_column?: string
  classification_status?: string
  sort_by?: EntitySortField
  sort_dir?: 'asc' | 'desc'
  page?: number
  page_size?: number
}
