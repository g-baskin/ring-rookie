"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  ArrowLeft,
  Bot,
  Calendar,
  Clock,
  Download,
  FileText,
  Loader2,
  Phone,
  User,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCall, type CallRecord } from "@/lib/api/calls";

function formatPhoneNumber(number: string): string {
  if (number.startsWith("+1") && number.length === 12) {
    return `(${number.slice(2, 5)}) ${number.slice(5, 8)}-${number.slice(8)}`;
  }
  return number;
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${String(seconds % 60).padStart(2, "0")}`;
}

function Detail({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="mt-1 text-sm font-medium">{children}</dd>
    </div>
  );
}

export default function CallDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const {
    data: call,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["call", id],
    queryFn: () => getCall(id),
  });

  function downloadTranscript(record: CallRecord) {
    if (!record.transcript) return;
    const url = URL.createObjectURL(new Blob([record.transcript], { type: "text/plain" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `transcript-${record.id}.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  if (isLoading) {
    return (
      <div className="flex min-h-64 items-center justify-center" aria-label="Loading call details">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !call) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" asChild>
          <Link href="/dashboard/calls">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Call History
          </Link>
        </Button>
        <Card className="border-destructive">
          <CardContent className="flex flex-col items-center py-16 text-center">
            <AlertCircle className="mb-3 h-12 w-12 text-destructive" />
            <h1 className="text-lg font-semibold">Call not available</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {error instanceof Error ? error.message : "This call could not be loaded."}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const counterpart = call.direction === "inbound" ? call.from_number : call.to_number;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/dashboard/calls" aria-label="Back to call history">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-xl font-semibold">Call details</h1>
            <p className="text-sm text-muted-foreground">
              {new Date(call.started_at).toLocaleString()}
            </p>
          </div>
        </div>
        <Badge variant={call.status === "completed" ? "default" : "secondary"}>
          {call.status.replaceAll("_", " ")}
        </Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <Detail label="Agent">
              <span className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                {call.agent_name ?? "Unknown agent"}
              </span>
            </Detail>
            <Detail label="Caller">
              <span className="flex items-center gap-2">
                <User className="h-4 w-4" />
                {call.contact_name ?? formatPhoneNumber(counterpart)}
              </span>
            </Detail>
            <Detail label="Direction">
              <span className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                {call.direction}
              </span>
            </Detail>
            <Detail label="Duration">
              <span className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                {formatDuration(call.duration_seconds)}
              </span>
            </Detail>
            <Detail label="Started">
              <span className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                {new Date(call.started_at).toLocaleString()}
              </span>
            </Detail>
            <Detail label="Workspace">{call.workspace_name ?? "No workspace"}</Detail>
            <Detail label="Provider">{call.provider}</Detail>
            <Detail label="Call ID">
              <span className="break-all font-mono text-xs">{call.id}</span>
            </Detail>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex-row items-center justify-between space-y-0">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="h-4 w-4" />
            Transcript
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            disabled={!call.transcript}
            onClick={() => downloadTranscript(call)}
          >
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
        </CardHeader>
        <CardContent>
          {call.transcript ? (
            <pre className="max-h-[55vh] overflow-auto whitespace-pre-wrap rounded-md border bg-muted/30 p-4 font-sans text-sm leading-relaxed">
              {call.transcript}
            </pre>
          ) : (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No transcript is available for this call.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
