"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { getIngestStatus, triggerSync } from "@/lib/api";
import type { SyncResponse } from "@/lib/types";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";

export default function SyncPage() {
  const statusQuery = useQuery({
    queryKey: ["ingest-status"],
    queryFn: getIngestStatus,
    refetchInterval: 60_000,
  });

  const syncMutation = useMutation({
    mutationFn: triggerSync,
  });

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Data Synchronisation</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage EU and UN sanctions list ingestion.
        </p>
      </div>

      {/* Status section */}
      <section className="space-y-4">
        <h2 className="text-base font-semibold text-slate-800">
          Current Status
        </h2>

        {statusQuery.isError && (
          <Alert variant="destructive">
            <AlertTitle>Failed to load status</AlertTitle>
            <AlertDescription>
              {statusQuery.error instanceof Error
                ? statusQuery.error.message
                : "An unexpected error occurred."}
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {statusQuery.isLoading &&
            ["EU", "UN"].map((label) => (
              <Card key={label}>
                <CardHeader>
                  <CardTitle className="text-sm">{label} List</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-3 w-32" />
                </CardContent>
              </Card>
            ))}

          {statusQuery.data?.lists.map((list) => (
            <Card key={list.source_list}>
              <CardHeader>
                <CardTitle className="text-sm">{list.source_list} List</CardTitle>
                <CardDescription>
                  {list.entry_count.toLocaleString()} entries
                </CardDescription>
              </CardHeader>
              <CardContent className="text-xs text-slate-500">
                {list.last_synced_at
                  ? `Last synced: ${new Date(list.last_synced_at).toLocaleString()}`
                  : "Never synced"}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <Separator />

      {/* Trigger section */}
      <section className="space-y-4">
        <div>
          <h2 className="text-base font-semibold text-slate-800">
            Trigger Sync
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Download and re-import all sanctions lists from their official
            sources. This may take several minutes.
          </p>
        </div>

        <Button
          onClick={() => syncMutation.mutate()}
          disabled={syncMutation.isPending}
        >
          {syncMutation.isPending ? "Syncing…" : "Sync Now"}
        </Button>

        {syncMutation.isError && (
          <Alert variant="destructive">
            <AlertTitle>Sync failed</AlertTitle>
            <AlertDescription>
              {syncMutation.error instanceof Error
                ? syncMutation.error.message
                : "An unexpected error occurred."}
            </AlertDescription>
          </Alert>
        )}

        {syncMutation.data && (
          <SyncResultCard result={syncMutation.data} />
        )}
      </section>
    </div>
  );
}

function SyncResultCard({ result }: { result: SyncResponse }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm text-green-700">Sync complete</CardTitle>
        <CardDescription>
          {result.total_inserted.toLocaleString()} entries inserted in total
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        {result.results.map((r) => (
          <div
            key={r.source_list}
            className="flex items-center justify-between rounded-md border bg-slate-50 px-3 py-2"
          >
            <span className="font-medium">{r.source_list}</span>
            <span className="text-slate-600">
              {r.inserted.toLocaleString()} entries &middot;{" "}
              {r.duration_seconds.toFixed(1)} s
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
