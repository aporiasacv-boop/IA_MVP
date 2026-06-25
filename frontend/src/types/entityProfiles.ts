export interface MonthlyBucket {
  movements: number
  amount: number
  debit?: number
  credit?: number
}

export interface RelatedAccountItem {
  code: string
  name: string
  movements: number
  amount: number
}

export interface RelatedCounterpartyItem {
  code: string
  name: string
  dimension: string
  movements: number
  amount: number
}

export interface EntityProfileItem {
  profile_id: number
  canonical_id: number
  canonical_name: string
  primary_rfc?: string | null
  total_movements: number
  total_amount: number
  average_amount: number
  first_seen?: string | null
  last_seen?: string | null
  active_months: number
  active_days: number
  debit_amount: number
  credit_amount: number
  debit_credit_ratio?: number | null
  related_accounts_count: number
  related_counterparties_count: number
  monthly_distribution: Record<string, MonthlyBucket>
  currencies: string[]
  journals: { distinct_count?: number; top?: Array<{ numero: string; movements: number }> }
  dimensions_used: string[]
  top_accounts: RelatedAccountItem[]
  top_counterparties: RelatedCounterpartyItem[]
  profile_completeness: number
  generated_at: string
  updated_at: string
}

export interface EntityProfileListResponse {
  items: EntityProfileItem[]
  total: number
  page: number
  page_size: number
}

export interface EntityProfileStatistics {
  entity_profiles_total: number
  canonical_entities_total: number
  profiles_without_movements: number
  average_profile_completeness: number
  profile_generation_time: number
  last_profile_refresh?: string | null
  total_movements_profiled: number
  average_movements_per_profile: number
}
