"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  MessageSquare,
  Download,
  Brain,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  BarChart3,
  Eye,
  Sparkles,
  CheckCircle2,
  XCircle,
  Lightbulb,
} from "lucide-react";
import {
  listConversations,
  exportConversations,
  analyzeConversations,
  getConversation,
  type ConversationRecord,
  type ConversationAnalysisResponse,
} from "@/lib/api/conversations";
import { api } from "@/lib/api";

interface Agent {
  id: string;
  name: string;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function getStatusBadgeVariant(
  status: string
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "active":
      return "default";
    case "ended":
      return "secondary";
    case "error":
      return "destructive";
    default:
      return "outline";
  }
}

export default function ConversationsPage() {
  const [page, setPage] = useState(1);
  const [selectedAgentId, setSelectedAgentId] = useState<string>("all");
  const [selectedConversations, setSelectedConversations] = useState<Set<string>>(new Set());
  const [selectAll, setSelectAll] = useState(false);
  const [analysisOpen, setAnalysisOpen] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<ConversationAnalysisResponse | null>(null);
  const [transcriptOpen, setTranscriptOpen] = useState(false);
  const [selectedTranscript, setSelectedTranscript] = useState<ConversationRecord | null>(null);

  // Fetch agents for filter
  const { data: agents = [] } = useQuery<Agent[]>({
    queryKey: ["agents"],
    queryFn: async () => {
      const response = await api.get("/api/v1/agents");
      return response.data;
    },
  });

  // Fetch conversations
  const {
    data: conversationsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["conversations", page, selectedAgentId],
    queryFn: () =>
      listConversations({
        page,
        page_size: 20,
        agent_id: selectedAgentId !== "all" ? selectedAgentId : undefined,
      }),
  });

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: (format: "csv" | "json") =>
      exportConversations({
        format,
        conversation_ids:
          selectedConversations.size > 0 ? Array.from(selectedConversations) : undefined,
        agent_id: selectedAgentId !== "all" ? selectedAgentId : undefined,
        include_messages: true,
      }),
    onSuccess: (blob, format) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `conversations_export.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  // Analyze mutation
  const analyzeMutation = useMutation({
    mutationFn: () =>
      analyzeConversations({
        conversation_ids:
          selectedConversations.size > 0 ? Array.from(selectedConversations) : undefined,
        agent_id: selectedAgentId !== "all" ? selectedAgentId : undefined,
      }),
    onSuccess: (data) => {
      setAnalysisResult(data);
      setAnalysisOpen(true);
    },
  });

  // Fetch transcript mutation
  const transcriptMutation = useMutation({
    mutationFn: (conversationId: string) => getConversation(conversationId),
    onSuccess: (data) => {
      setSelectedTranscript(data);
      setTranscriptOpen(true);
    },
  });

  const conversations = conversationsData?.conversations ?? [];
  const totalPages = conversationsData?.total_pages ?? 0;
  const total = conversationsData?.total ?? 0;

  const handleSelectAll = (checked: boolean) => {
    setSelectAll(checked);
    if (checked) {
      setSelectedConversations(new Set(conversations.map((c) => c.id)));
    } else {
      setSelectedConversations(new Set());
    }
  };

  const handleSelectConversation = (conversationId: string, checked: boolean) => {
    const newSelected = new Set(selectedConversations);
    if (checked) {
      newSelected.add(conversationId);
    } else {
      newSelected.delete(conversationId);
    }
    setSelectedConversations(newSelected);
    setSelectAll(newSelected.size === conversations.length && conversations.length > 0);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Chat History</h1>
          <p className="text-sm text-muted-foreground">View and analyze Chat Champ conversations</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link href="/dashboard/conversations/analytics">
              <BarChart3 className="mr-2 h-4 w-4" />
              Analytics
            </Link>
          </Button>
        </div>
      </div>

      {/* Filters and Actions */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-medium">Conversations</CardTitle>
            <div className="flex items-center gap-2">
              <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Agents" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Agents</SelectItem>
                  {agents.map((agent) => (
                    <SelectItem key={agent.id} value={agent.id}>
                      {agent.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" disabled={exportMutation.isPending}>
                    {exportMutation.isPending ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Download className="mr-2 h-4 w-4" />
                    )}
                    Export {selectedConversations.size > 0 && `(${selectedConversations.size})`}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => exportMutation.mutate("csv")}>
                    Export as CSV
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => exportMutation.mutate("json")}>
                    Export as JSON
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Button
                variant="outline"
                size="sm"
                onClick={() => analyzeMutation.mutate()}
                disabled={analyzeMutation.isPending}
              >
                {analyzeMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Brain className="mr-2 h-4 w-4" />
                )}
                Analyze
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="mb-4 h-16 w-16 animate-spin text-muted-foreground/50" />
              <p className="text-muted-foreground">Loading conversations...</p>
            </div>
          ) : error instanceof Error ? (
            <div className="flex flex-col items-center justify-center py-16">
              <AlertCircle className="mb-4 h-16 w-16 text-destructive" />
              <h3 className="mb-2 text-lg font-semibold">Failed to load conversations</h3>
              <p className="max-w-sm text-center text-sm text-muted-foreground">{error.message}</p>
            </div>
          ) : conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <MessageSquare className="mb-4 h-16 w-16 text-muted-foreground/50" />
              <h3 className="mb-2 text-lg font-semibold">No conversations yet</h3>
              <p className="max-w-sm text-center text-sm text-muted-foreground">
                Conversations will appear here once your chat agents start receiving messages.
              </p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <Checkbox
                        checked={selectAll}
                        onCheckedChange={(checked) => handleSelectAll(!!checked)}
                      />
                    </TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Agent</TableHead>
                    <TableHead>Messages</TableHead>
                    <TableHead>Tokens</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {conversations.map((conversation) => (
                    <TableRow key={conversation.id}>
                      <TableCell>
                        <Checkbox
                          checked={selectedConversations.has(conversation.id)}
                          onCheckedChange={(checked) =>
                            handleSelectConversation(conversation.id, !!checked)
                          }
                        />
                      </TableCell>
                      <TableCell className="text-sm">
                        {formatDate(conversation.started_at)}
                      </TableCell>
                      <TableCell className="font-medium">
                        {conversation.agent_name ?? "Unknown"}
                      </TableCell>
                      <TableCell>{conversation.message_count}</TableCell>
                      <TableCell>{conversation.total_tokens.toLocaleString()}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(conversation.status)}>
                          {conversation.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => transcriptMutation.mutate(conversation.id)}
                          disabled={transcriptMutation.isPending}
                        >
                          {transcriptMutation.isPending &&
                          transcriptMutation.variables === conversation.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="mt-4 flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * 20 + 1}-{Math.min(page * 20, total)} of {total}{" "}
                  conversations
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    Page {page} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Transcript Sheet */}
      <Sheet open={transcriptOpen} onOpenChange={setTranscriptOpen}>
        <SheetContent className="w-[500px] overflow-y-auto sm:max-w-[500px]">
          <SheetHeader>
            <SheetTitle>Conversation Transcript</SheetTitle>
            <SheetDescription>
              {selectedTranscript?.agent_name ?? "Unknown Agent"} -{" "}
              {selectedTranscript?.message_count ?? 0} messages
            </SheetDescription>
          </SheetHeader>
          <div className="mt-4 space-y-3">
            {selectedTranscript?.messages?.map((message) => (
              <div
                key={message.id}
                className={`rounded-lg p-3 ${
                  message.role === "assistant" ? "ml-4 bg-primary/10" : "mr-4 bg-muted"
                }`}
              >
                <div className="mb-1 flex items-center gap-2">
                  <span className="text-xs font-medium uppercase text-muted-foreground">
                    {message.role}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(message.created_at).toLocaleTimeString()}
                  </span>
                </div>
                <p className="whitespace-pre-wrap text-sm">{message.content}</p>
              </div>
            ))}
          </div>
        </SheetContent>
      </Sheet>

      {/* Analysis Sheet */}
      <Sheet open={analysisOpen} onOpenChange={setAnalysisOpen}>
        <SheetContent className="w-[600px] overflow-y-auto sm:max-w-[600px]">
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-amber-500" />
              Conversation Analysis
            </SheetTitle>
            <SheetDescription>
              AI-generated insights from {analysisResult?.total_conversations_analyzed ?? 0}{" "}
              conversations
            </SheetDescription>
          </SheetHeader>

          {analysisResult && (
            <div className="mt-6 space-y-6">
              {/* Stats */}
              <div className="flex gap-4 text-sm">
                <div className="rounded bg-muted px-3 py-2">
                  <span className="text-muted-foreground">Messages: </span>
                  <span className="font-medium">{analysisResult.total_messages}</span>
                </div>
                <div className="rounded bg-muted px-3 py-2">
                  <span className="text-muted-foreground">Tokens: </span>
                  <span className="font-medium">
                    {analysisResult.total_tokens.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Patterns */}
              <div>
                <h3 className="mb-3 flex items-center gap-2 font-medium">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Patterns Found
                </h3>
                <ul className="space-y-2">
                  {analysisResult.patterns.map((pattern, i) => (
                    <li key={i} className="rounded-lg bg-emerald-500/10 p-3 text-sm">
                      {pattern}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Issues */}
              <div>
                <h3 className="mb-3 flex items-center gap-2 font-medium">
                  <XCircle className="h-4 w-4 text-red-500" />
                  Issues Identified
                </h3>
                <ul className="space-y-2">
                  {analysisResult.issues.map((issue, i) => (
                    <li key={i} className="rounded-lg bg-red-500/10 p-3 text-sm">
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Suggestions */}
              <div>
                <h3 className="mb-3 flex items-center gap-2 font-medium">
                  <Lightbulb className="h-4 w-4 text-amber-500" />
                  Suggestions
                </h3>
                <ul className="space-y-2">
                  {analysisResult.suggestions.map((suggestion, i) => (
                    <li key={i} className="rounded-lg bg-amber-500/10 p-3 text-sm">
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Sample Improvements */}
              {analysisResult.sample_improvements && (
                <div>
                  <h3 className="mb-3 font-medium">Suggested Prompt Improvements</h3>
                  <div className="rounded-lg border bg-muted/50 p-4">
                    <pre className="whitespace-pre-wrap font-mono text-xs">
                      {analysisResult.sample_improvements}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
