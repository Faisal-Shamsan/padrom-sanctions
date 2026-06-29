"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { getHistory } from "@/lib/api";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const PAGE_SIZE = 20;

export default function HistoryPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["history", page],
    queryFn: () => getHistory(page, PAGE_SIZE),
    staleTime: 0,
    placeholderData: (prev) => prev,
  });

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 1;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Screening History</h1>
        <p className="mt-1 text-sm text-slate-500">
          Audit log of all sanctions screening requests.
        </p>
      </div>

      {isError && (
        <Alert variant="destructive">
          <AlertTitle>Failed to load history</AlertTitle>
          <AlertDescription>
            {error instanceof Error
              ? error.message
              : "An unexpected error occurred."}
          </AlertDescription>
        </Alert>
      )}

      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Queried Name</TableHead>
              <TableHead>External ID</TableHead>
              <TableHead>Result</TableHead>
              <TableHead>Score</TableHead>
              <TableHead>Date</TableHead>
              <TableHead className="text-right">Duration</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading &&
              Array.from({ length: PAGE_SIZE }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 6 }).map((_, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            {data?.items.map((item) => (
              <TableRow key={item.screening_id}>
                <TableCell className="font-medium">
                  {item.queried_name}
                </TableCell>
                <TableCell className="text-slate-500">
                  {item.external_id}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={
                      item.result === "POTENTIAL_MATCH"
                        ? "destructive"
                        : "secondary"
                    }
                  >
                    {item.result === "POTENTIAL_MATCH"
                      ? "POTENTIAL MATCH"
                      : "NO MATCH"}
                  </Badge>
                </TableCell>
                <TableCell>
                  {item.result === "POTENTIAL_MATCH"
                    ? `${Math.round(item.score * 100)}%`
                    : "—"}
                </TableCell>
                <TableCell className="text-slate-500 text-xs">
                  {new Date(item.screened_at).toLocaleString()}
                </TableCell>
                <TableCell className="text-right text-slate-500 text-xs">
                  {item.duration_ms} ms
                </TableCell>
              </TableRow>
            ))}
            {data?.items.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-center text-slate-400 py-8"
                >
                  No screening records found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {data && totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-slate-600">
          <span>
            Page {data.page} of {totalPages} &mdash; {data.total} total records
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
