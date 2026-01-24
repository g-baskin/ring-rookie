"use client";

import { useState, useMemo, useRef } from "react";
import { useDebounce } from "use-debounce";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  History,
  Download,
  Play,
  Pause,
  Loader2,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Brain,
  BarChart3,
  FileJson,
  FileSpreadsheet,
  Lightbulb,
  AlertTriangle,
  Target,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  listCalls,
  exportCalls,
  analyzeCalls,
  type CallRecord,
  type CallAnalysisResponse,
} from "@/lib/api/calls";
import { api } from "@/lib/api";
import { FolderOpen } from "lucide-react";
import Link from "next/link";

interface Workspace {
  id: string;
  name: string;
  description: string | null;
  is_default: boolean;
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins === 0) return `${secs}s`;
  return `${mins}m ${secs}s`;
}

function formatPhoneNumber(number: string): string {
  if (number.startsWith("+1") && number.length === 12) {
    return `(${number.slice(2, 5)}) ${number.slice(5, 8)}-${number.slice(8)}`;
  }
  return number;
}

export default function CallHistoryPage() {
  const router = useRouter();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playingCallId, setPlayingCallId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearchQuery] = useDebounce(searchQuery, 300);
  const [statusFilter, setStatusFilter] = useState("all");
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string>("all");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Selection state
  const [selectedCalls, setSelectedCalls] = useState<Set<string>>(new Set());
  const [selectAll, setSelectAll] = useState(false);

  // Analysis sheet state
  const [analysisOpen, setAnalysisOpen] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<CallAnalysisResponse | null>(null);

  // Fetch workspaces
  const { data: workspaces = [] } = useQuery<Workspace[]>({
    queryKey: ["workspaces"],
    queryFn: async () => {
      const response = await api.get("/api/v1/workspaces");
      return response.data;
    },
  });

  // Fetch calls from API
  const { data, isLoading, error } = useQuery({
    queryKey: ["calls", page, statusFilter, selectedWorkspaceId],
    queryFn: () =>
      listCalls({
        page,
        page_size: pageSize,
        workspace_id: selectedWorkspaceId !== "all" ? selectedWorkspaceId : undefined,
        status:
          statusFilter !== "all" && !["inbound", "outbound"].includes(statusFilter)
            ? statusFilter
            : undefined,
        direction: ["inbound", "outbound"].includes(statusFilter)
          ? (statusFilter as "inbound" | "outbound")
          : undefined,
      }),
  });

  const callsData = useMemo(() => data?.calls ?? [], [data?.calls]);
  const totalPages = data?.total_pages ?? 0;
  const totalCalls = data?.total ?? 0;

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: async (format: "csv" | "json") => {
      const blob = await exportCalls({
        format,
        call_ids: selectedCalls.size > 0 ? Array.from(selectedCalls) : undefined,
        include_transcripts: true,
      });
      return { blob, format };
    },
    onSuccess: ({ blob, format }) => {
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `calls_export.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      toast.success(`Exported ${selectedCalls.size || "all"} calls as ${format.toUpperCase()}`);
    },
    onError: (error: Error) => {
      toast.error(`Export failed: ${error.message}`);
    },
  });

  // Analysis mutation
  const analysisMutation = useMutation({
    mutationFn: async () => {
      return analyzeCalls({
        call_ids: selectedCalls.size > 0 ? Array.from(selectedCalls) : undefined,
      });
    },
    onSuccess: (result) => {
      setAnalysisResult(result);
      setAnalysisOpen(true);
    },
    onError: (error: Error) => {
      toast.error(`Analysis failed: ${error.message}`);
    },
  });

  // Selection handlers
  const handleSelectAll = (checked: boolean) => {
    setSelectAll(checked);
    if (checked) {
      setSelectedCalls(new Set(filteredCalls.map((c) => c.id)));
    } else {
      setSelectedCalls(new Set());
    }
  };

  const handleSelectCall = (callId: string, checked: boolean) => {
    const newSelected = new Set(selectedCalls);
    if (checked) {
      newSelected.add(callId);
    } else {
      newSelected.delete(callId);
    }
    setSelectedCalls(newSelected);
    setSelectAll(newSelected.size === filteredCalls.length && filteredCalls.length > 0);
  };

  const handlePlayRecording = (call: CallRecord) => {
    if (!call.recording_url) {
      toast.error("No recording available for this call");
      return;
    }

    // If already playing this call, pause it
    if (playingCallId === call.id && audioRef.current) {
      audioRef.current.pause();
      setPlayingCallId(null);
      return;
    }

    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause();
    }

    // Create new audio element and play
    const audio = new Audio(call.recording_url);
    audioRef.current = audio;
    setPlayingCallId(call.id);

    audio.play().catch((err: Error) => {
      toast.error(`Failed to play recording: ${err.message}`);
      setPlayingCallId(null);
    });

    audio.onended = () => {
      setPlayingCallId(null);
    };
  };

  const handleDownloadTranscript = (call: CallRecord) => {
    if (!call.transcript) {
      toast.error("No transcript available for this call");
      return;
    }

    // Create a blob with the transcript text
    const blob = new Blob([call.transcript], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `transcript-${call.id}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success("Transcript download started");
  };

  const handleRowClick = (callId: string) => {
    router.push(`/dashboard/calls/${callId}`);
  };

  // Filter calls by search query (client-side for now)
  const filteredCalls = useMemo(() => {
    if (!debouncedSearchQuery) return callsData;
    return callsData.filter((call) => {
      const searchLower = debouncedSearchQuery.toLowerCase();
      return (
        (call.agent_name?.toLowerCase().includes(searchLower) ?? false) ||
        (call.contact_name?.toLowerCase().includes(searchLower) ?? false) ||
        call.from_number.includes(debouncedSearchQuery) ||
        call.to_number.includes(debouncedSearchQuery)
      );
    });
  }, [callsData, debouncedSearchQuery]);

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "completed":
        return "default";
      case "failed":
      case "busy":
      case "no_answer":
        return "destructive";
      case "in_progress":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Call History</h1>
          <p className="text-sm text-muted-foreground">
            {isLoading
              ? "Loading..."
              : totalCalls === 0
                ? "No calls yet"
                : `${totalCalls} total calls`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Input
            placeholder="Search calls..."
            className="w-[200px]"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {workspaces.length > 0 && (
            <Select
              value={selectedWorkspaceId}
              onValueChange={(value) => {
                setSelectedWorkspaceId(value);
                setPage(1);
                const wsName =
                  value === "all"
                    ? "All Workspaces"
                    : workspaces.find((ws) => ws.id === value)?.name;
                toast.info(`Switched to ${wsName}`);
              }}
            >
              <SelectTrigger className="h-8 w-[220px] text-sm">
                <FolderOpen className="mr-2 h-3.5 w-3.5" />
                <SelectValue placeholder="All Workspaces" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Workspaces (Admin)</SelectItem>
                {workspaces.map((ws) => (
                  <SelectItem key={ws.id} value={ws.id}>
                    {ws.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          <Select
            value={statusFilter}
            onValueChange={(value) => {
              setStatusFilter(value);
              setPage(1);
            }}
          >
            <SelectTrigger className="h-8 w-[130px] text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Calls</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="in_progress">In Progress</SelectItem>
              <SelectItem value="inbound">Inbound</SelectItem>
              <SelectItem value="outbound">Outbound</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Action toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {selectedCalls.size > 0 && (
            <Badge variant="secondary" className="py-1">
              {selectedCalls.size} selected
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Analytics link */}
          <Button variant="outline" size="sm" asChild>
            <Link href="/dashboard/calls/analytics">
              <BarChart3 className="mr-2 h-4 w-4" />
              Analytics
            </Link>
          </Button>

          {/* Export dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" disabled={exportMutation.isPending}>
                {exportMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 h-4 w-4" />
                )}
                Export {selectedCalls.size > 0 ? `(${selectedCalls.size})` : "All"}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => exportMutation.mutate("csv")}>
                <FileSpreadsheet className="mr-2 h-4 w-4" />
                Export as CSV
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => exportMutation.mutate("json")}>
                <FileJson className="mr-2 h-4 w-4" />
                Export as JSON
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Analyze button */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => analysisMutation.mutate()}
            disabled={
              analysisMutation.isPending || (selectedCalls.size > 0 && selectedCalls.size < 3)
            }
            title={
              selectedCalls.size > 0 && selectedCalls.size < 3
                ? "Select at least 3 calls for analysis"
                : undefined
            }
          >
            {analysisMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Brain className="mr-2 h-4 w-4" />
            )}
            Analyze {selectedCalls.size > 0 ? `(${selectedCalls.size})` : "All"}
          </Button>
        </div>
      </div>

      <Card>
        <CardContent>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="mb-4 h-16 w-16 animate-spin text-muted-foreground/50" />
              <p className="text-muted-foreground">Loading calls...</p>
            </div>
          ) : error instanceof Error ? (
            <div className="flex flex-col items-center justify-center py-16">
              <AlertCircle className="mb-4 h-16 w-16 text-destructive" />
              <h3 className="mb-2 text-lg font-semibold">Failed to load calls</h3>
              <p className="max-w-sm text-center text-sm text-muted-foreground">{error.message}</p>
            </div>
          ) : callsData.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <History className="mb-4 h-16 w-16 text-muted-foreground/50" />
              <h3 className="mb-2 text-lg font-semibold">No calls yet</h3>
              <p className="max-w-sm text-center text-sm text-muted-foreground">
                Call history will appear here once your voice agents start handling calls
              </p>
            </div>
          ) : filteredCalls.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <History className="mb-4 h-16 w-16 text-muted-foreground/50" />
              <h3 className="mb-2 text-lg font-semibold">No matching calls found</h3>
              <p className="max-w-sm text-center text-sm text-muted-foreground">
                Try adjusting your search or filter criteria
              </p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[40px]">
                      <Checkbox
                        checked={selectAll}
                        onCheckedChange={handleSelectAll}
                        aria-label="Select all calls"
                      />
                    </TableHead>
                    <TableHead>Date & Time</TableHead>
                    <TableHead>Agent</TableHead>
                    <TableHead>Direction</TableHead>
                    <TableHead>From/To</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[100px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredCalls.map((call) => (
                    <TableRow
                      key={call.id}
                      className="cursor-pointer"
                      onClick={() => handleRowClick(call.id)}
                      data-selected={selectedCalls.has(call.id)}
                    >
                      <TableCell>
                        <Checkbox
                          checked={selectedCalls.has(call.id)}
                          onCheckedChange={(checked) =>
                            handleSelectCall(call.id, checked as boolean)
                          }
                          onClick={(e) => e.stopPropagation()}
                          aria-label={`Select call ${call.id}`}
                        />
                      </TableCell>
                      <TableCell className="text-sm">
                        {new Date(call.started_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="font-medium">
                        {call.agent_name ?? "Unknown Agent"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={call.direction === "inbound" ? "default" : "secondary"}>
                          {call.direction}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {call.direction === "inbound"
                          ? formatPhoneNumber(call.from_number)
                          : formatPhoneNumber(call.to_number)}
                        {call.contact_name && (
                          <span className="ml-2 text-muted-foreground">({call.contact_name})</span>
                        )}
                      </TableCell>
                      <TableCell>{formatDuration(call.duration_seconds)}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(call.status)}>
                          {call.status.replace("_", " ")}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {call.recording_url && (
                            <Button
                              variant="ghost"
                              size="icon"
                              title={
                                playingCallId === call.id ? "Pause recording" : "Play recording"
                              }
                              onClick={(e) => {
                                e.stopPropagation();
                                handlePlayRecording(call);
                              }}
                            >
                              {playingCallId === call.id ? (
                                <Pause className="h-4 w-4" />
                              ) : (
                                <Play className="h-4 w-4" />
                              )}
                            </Button>
                          )}
                          {call.transcript && (
                            <Button
                              variant="ghost"
                              size="icon"
                              title="Download transcript"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDownloadTranscript(call);
                              }}
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-4 flex items-center justify-between border-t pt-4">
                  <p className="text-sm text-muted-foreground">
                    Page {page} of {totalPages}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="mr-1 h-4 w-4" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      Next
                      <ChevronRight className="ml-1 h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Analysis Results Sheet */}
      <Sheet open={analysisOpen} onOpenChange={setAnalysisOpen}>
        <SheetContent className="w-[600px] sm:max-w-[600px]">
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Call Analysis Report
            </SheetTitle>
            <SheetDescription>
              {analysisResult
                ? `Analyzed ${analysisResult.total_calls_analyzed} calls (${formatDuration(analysisResult.total_duration_seconds)} total)`
                : "AI-powered insights to improve your voice agent"}
            </SheetDescription>
          </SheetHeader>

          {analysisResult && (
            <ScrollArea className="h-[calc(100vh-140px)] pr-4">
              <div className="mt-6 space-y-6">
                {/* Patterns Section */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Target className="h-4 w-4 text-blue-500" />
                      Patterns Found
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {analysisResult.patterns.map((pattern, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500" />
                          {pattern}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {/* Issues Section */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <AlertTriangle className="h-4 w-4 text-amber-500" />
                      Issues Identified
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {analysisResult.issues.map((issue, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                          {issue}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {/* Suggestions Section */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Lightbulb className="h-4 w-4 text-emerald-500" />
                      Suggestions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {analysisResult.suggestions.map((suggestion, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {/* Sample Improvements Section */}
                {analysisResult.sample_improvements && (
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base">Suggested Prompt Changes</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="whitespace-pre-wrap rounded-md bg-muted p-4 font-mono text-sm">
                        {analysisResult.sample_improvements}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </ScrollArea>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
