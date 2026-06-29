"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { screenEntity } from "@/lib/api";
import type { ScreenEntityResponse } from "@/lib/types";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

const schema = z.object({
  external_id: z.string().min(1, "External ID is required"),
  name: z.string().min(2, "Name must be at least 2 characters"),
});

type FormValues = z.infer<typeof schema>;

export default function ScreenPage() {
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { external_id: "", name: "" },
  });

  const mutation = useMutation({
    mutationFn: (values: FormValues) => screenEntity(values),
  });

  function onSubmit(values: FormValues) {
    mutation.mutate(values);
  }

  const result = mutation.data;

  return (
    <div className="space-y-6 max-w-lg">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Screen Entity</h1>
        <p className="mt-1 text-sm text-slate-500">
          Check a counterparty name against EU and UN sanctions lists.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Counterparty details</CardTitle>
          <CardDescription>
            Enter the external reference and the name to screen.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="external_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>External ID</FormLabel>
                    <FormControl>
                      <Input placeholder="POL-001" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Full legal name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? "Screening…" : "Screen"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {mutation.isError && (
        <Alert variant="destructive">
          <AlertTitle>Screening failed</AlertTitle>
          <AlertDescription>
            {mutation.error instanceof Error
              ? mutation.error.message
              : "An unexpected error occurred."}
          </AlertDescription>
        </Alert>
      )}

      {result && <ScreeningResult result={result} />}
    </div>
  );
}

function ScreeningResult({ result }: { result: ScreenEntityResponse }) {
  const isMatch = result.result === "POTENTIAL_MATCH";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Result
          <Badge variant={isMatch ? "destructive" : "secondary"}>
            {isMatch ? "POTENTIAL MATCH" : "NO MATCH"}
          </Badge>
        </CardTitle>
        <CardDescription>
          Screened at {new Date(result.screened_at).toLocaleString()} &middot;{" "}
          {result.duration_ms} ms
        </CardDescription>
      </CardHeader>
      {isMatch && (
        <CardContent className="space-y-3 text-sm">
          {result.score > 0 && (
            <div className="flex gap-2">
              <span className="font-medium text-slate-600">Score:</span>
              <span>{Math.round(result.score * 100)}%</span>
            </div>
          )}
          {result.matched_entry && (
            <div className="rounded-md border bg-amber-50 p-3 space-y-1">
              <p className="font-medium text-amber-900">
                {result.matched_entry.primary_name}
              </p>
              <p className="text-xs text-amber-700">
                List: {result.matched_entry.source_list}
              </p>
              <p className="text-xs text-amber-700">
                Entry ID: {result.matched_entry.entry_id}
              </p>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}
