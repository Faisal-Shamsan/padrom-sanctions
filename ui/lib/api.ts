import type { ScreenEntityRequest, ScreenEntityResponse } from "./types";

// Base URL is set at build time via NEXT_PUBLIC_API_URL.
// The fallback is only used in local dev without a .env.local.
const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Internal helper — centralises error handling and JSON parsing
// ---------------------------------------------------------------------------
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!res.ok) {
    // Surface the API error body if available, otherwise fall back to status text
    let message = `API error ${res.status}: ${res.statusText}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // ignore JSON parse failure
    }
    throw new Error(message);
  }

  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Public API functions — one per endpoint
// ---------------------------------------------------------------------------

/** GET /health — used by the home page to show API reachability. */
export async function getHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/health");
}

/**
 * POST /v1/screen/entity — submit a counterparty for sanctions screening.
 * Endpoint not yet implemented; will return 404 until Sprint 2.
 */
export async function screenEntity(
  payload: ScreenEntityRequest,
): Promise<ScreenEntityResponse> {
  return request<ScreenEntityResponse>("/v1/screen/entity", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
