// TypeScript types mirroring the Pydantic schemas defined in api/src/.
// Keep these in sync manually until OpenAPI codegen is set up.

export type EntityType =
  | "policyholder"
  | "claimant"
  | "broker"
  | "supplier"
  | "reinsurer";

export interface ScreenEntityRequest {
  name: string;
  entity_type: EntityType;
  /** ISO 3166-1 alpha-2 country code — optional, improves match precision */
  country_code?: string;
  /** Opaque reference from the core insurance system for audit tracing */
  reference_id?: string;
}

export type MatchStatus = "clear" | "potential_match" | "confirmed_match";

export interface ScreenEntityResponse {
  screening_id: string;
  status: MatchStatus;
  matches: SanctionMatch[];
  screened_at: string; // ISO 8601 timestamp
}

export interface SanctionMatch {
  list_name: string; // e.g. "EU Consolidated" | "UN SCSL"
  entity_name: string;
  score: number; // 0–100 RapidFuzz partial ratio
  entry_id: string; // unique ID within the source list
}
