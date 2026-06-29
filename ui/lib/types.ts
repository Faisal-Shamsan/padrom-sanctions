// TypeScript types mirroring the Pydantic schemas defined in api/src/.
// Keep these in sync manually until OpenAPI codegen is set up.

// Screening
export interface ScreenEntityRequest {
  external_id: string;
  name: string;
}

export interface MatchedEntry {
  entry_id: string;
  primary_name: string;
  source_list: string;
  score: number;
}

export interface ScreenEntityResponse {
  screening_id: string;
  external_id: string;
  result: "POTENTIAL_MATCH" | "NO_MATCH";
  score: number;
  matched_entry: MatchedEntry | null;
  screened_at: string;
  duration_ms: number;
}

// History
export interface HistoryItem {
  screening_id: string;
  external_id: string;
  queried_name: string;
  result: "POTENTIAL_MATCH" | "NO_MATCH";
  score: number;
  screened_at: string;
  duration_ms: number;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

// Ingest
export interface ListSyncResult {
  source_list: string;
  inserted: number;
  duration_seconds: number;
}

export interface SyncResponse {
  results: ListSyncResult[];
  total_inserted: number;
}

export interface ListStatus {
  source_list: string;
  entry_count: number;
  last_synced_at: string | null;
}

export interface StatusResponse {
  lists: ListStatus[];
}
