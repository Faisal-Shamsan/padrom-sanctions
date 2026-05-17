"use client";

import { useQuery } from "@tanstack/react-query";
import { getHealth } from "@/lib/api";

export default function HomePage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    retry: false, // don't retry on network error — show status immediately
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          PADROM Sanctions Screening
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Proof-of-concept — EU Consolidated List &amp; UN Security Council List
        </p>
      </div>

      <div className="flex items-center gap-2 rounded-lg border bg-white p-4 text-sm shadow-sm">
        <span className="font-medium text-slate-700">API status:</span>
        {isLoading && (
          <span className="text-slate-400">checking&hellip;</span>
        )}
        {isError && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
            unreachable
          </span>
        )}
        {data && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
            {data.status}
          </span>
        )}
      </div>

      <p className="text-xs text-slate-400">
        Screening and audit features will appear here as sprints progress.
      </p>
    </div>
  );
}
