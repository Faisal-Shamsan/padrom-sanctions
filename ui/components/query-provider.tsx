"use client";

// TanStack Query requires a client-side Provider. This wrapper component keeps
// the root layout a React Server Component while still providing query context.

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  // useState ensures each browser session gets its own QueryClient instance,
  // preventing state from leaking between server renders.
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000, // 30 s — reasonable default for sanctions data
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
