Build a new UI feature for: $ARGUMENTS

## Data-flow chain

Every UI feature that involves user input follows this exact chain — do not skip steps
or add logic outside of it:

```
Zod schema
  → React Hook Form (useForm + zodResolver)
    → TanStack Query useMutation (or useQuery for reads)
      → lib/api.ts function
        → FastAPI endpoint
```

## 1. Define the Zod schema (validation only)

Create or extend a schema in the feature file or a dedicated `schemas.ts`:

```typescript
import { z } from "zod";

export const screenEntitySchema = z.object({
  name: z.string().min(1, "Name is required"),
  entity_type: z.enum(["policyholder", "claimant", "broker", "supplier", "reinsurer"]),
  country_code: z.string().length(2).optional(),
  reference_id: z.string().optional(),
});

export type ScreenEntityFormValues = z.infer<typeof screenEntitySchema>;
```

Zod is for **validation only** — no business logic here.

## 2. Wire up React Hook Form

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

const form = useForm<ScreenEntityFormValues>({
  resolver: zodResolver(screenEntitySchema),
  defaultValues: { name: "", entity_type: "policyholder" },
});
```

## 3. Call the API via TanStack Query

**Mutations** (POST/PUT/DELETE):
```typescript
import { useMutation } from "@tanstack/react-query";
import { screenEntity } from "@/lib/api";

const mutation = useMutation({
  mutationFn: screenEntity,
  onSuccess: (data) => { /* show results */ },
  onError: (error: Error) => { /* show error.message — already formatted by api.ts */ },
});

// In the form submit handler:
const onSubmit = (values: ScreenEntityFormValues) => {
  mutation.mutate(values);
};
```

**Queries** (GET):
```typescript
import { useQuery } from "@tanstack/react-query";

// Query key convention: flat array for simple; hierarchical for parameterised
const { data } = useQuery({
  queryKey: ["screen", { name, entityType }],   // hierarchical — preferred
  queryFn: () => screenEntity({ name, entity_type: entityType }),
  enabled: !!name,
});
```

## 4. Add a function to `lib/api.ts`

The `request<T>()` helper handles `Content-Type`, error parsing (`body.detail`), and JSON:

```typescript
export async function yourNewFunction(payload: YourRequest): Promise<YourResponse> {
  return request<YourResponse>("/v1/your/endpoint", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
```

## 5. Keep `lib/types.ts` in sync with Pydantic schemas

Types in `lib/types.ts` mirror the Pydantic schemas in `api/src/`. Until OpenAPI codegen
is set up, update them manually whenever the API contract changes.

Current types to be aware of:

```typescript
// Entity types (mirrors EntityType enum in API)
export type EntityType = "policyholder" | "claimant" | "broker" | "supplier" | "reinsurer";

export interface ScreenEntityRequest {
  name: string;
  entity_type: EntityType;
  country_code?: string;   // ISO 3166-1 alpha-2
  reference_id?: string;   // opaque audit reference
}

export type MatchStatus = "clear" | "potential_match" | "confirmed_match";

export interface ScreenEntityResponse {
  screening_id: string;
  status: MatchStatus;
  matches: SanctionMatch[];
  screened_at: string;     // ISO 8601
}

export interface SanctionMatch {
  list_name: string;       // "EU Consolidated" | "UN SCSL"
  entity_name: string;
  score: number;           // 0–100 RapidFuzz partial ratio
  entry_id: string;
}
```

## Environment variable

The only env var used in the UI is `NEXT_PUBLIC_API_URL`. It defaults to
`http://localhost:8000` in `lib/api.ts` — no changes needed for local dev.

## Rules

- **No business logic in the UI.** Zod handles validation; React renders results.
  If you find yourself computing match scores or filtering sanctions data in the UI, stop —
  that belongs in `api/src/screening/service.py`.
- **No `any` types.** TypeScript strict mode is on. Use `unknown` and narrow it.
- **No direct `fetch` calls** outside `lib/api.ts`. All HTTP goes through `request<T>()`.

## Checklist

- [ ] Zod schema defined for all form inputs
- [ ] `useForm` wired with `zodResolver`
- [ ] TanStack Query `useMutation` or `useQuery` used for API calls
- [ ] New API function added to `lib/api.ts` using `request<T>()`
- [ ] `lib/types.ts` updated if API contract changed
- [ ] No business logic in component files
- [ ] `pnpm lint` passes
- [ ] `pnpm typecheck` passes
