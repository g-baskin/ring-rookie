"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  BarChart3,
  DollarSign,
  AlertTriangle,
  TrendingUp,
  ArrowLeft,
  Loader2,
  AlertCircle,
  MessageSquare,
  Coins,
} from "lucide-react";
import { getConversationAnalytics } from "@/lib/api/conversations";
import { api } from "@/lib/api";

interface Agent {
  id: string;
  name: string;
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "N/A";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins === 0) return `${secs}s`;
  return `${mins}m ${secs}s`;
}

function getEfficiencyColor(rating: string): string {
  switch (rating) {
    case "efficient":
      return "bg-emerald-500";
    case "moderate":
      return "bg-amber-500";
    case "wasteful":
      return "bg-red-500";
    default:
      return "bg-gray-500";
  }
}

function getEfficiencyBadgeVariant(
  rating: string
): "default" | "secondary" | "destructive" | "outline" {
  switch (rating) {
    case "efficient":
      return "default";
    case "moderate":
      return "secondary";
    case "wasteful":
      return "destructive";
    default:
      return "outline";
  }
}

export default function ConversationAnalyticsPage() {
  const [selectedAgentId, setSelectedAgentId] = useState<string>("all");

  // Fetch agents for filter
  const { data: agents = [] } = useQuery<Agent[]>({
    queryKey: ["agents"],
    queryFn: async () => {
      const response = await api.get("/api/v1/agents");
      return response.data;
    },
  });

  // Fetch analytics
  const {
    data: analytics,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["conversation-analytics", selectedAgentId],
    queryFn: () =>
      getConversationAnalytics({
        agent_id: selectedAgentId !== "all" ? selectedAgentId : undefined,
      }),
  });

  // Get wasteful conversations for the table
  const wastefulConversations =
    analytics?.efficiency_scores.filter((s) => s.efficiency_rating === "wasteful") ?? [];

  // Calculate bar chart data
  const chartData = analytics
    ? [
        {
          label: "Efficient",
          value: analytics.conversations_by_efficiency.efficient,
          color: "bg-emerald-500",
          percentage:
            analytics.total_conversations > 0
              ? Math.round(
                  (analytics.conversations_by_efficiency.efficient / analytics.total_conversations) *
                    100
                )
              : 0,
        },
        {
          label: "Moderate",
          value: analytics.conversations_by_efficiency.moderate,
          color: "bg-amber-500",
          percentage:
            analytics.total_conversations > 0
              ? Math.round(
                  (analytics.conversations_by_efficiency.moderate / analytics.total_conversations) *
                    100
                )
              : 0,
        },
        {
          label: "Wasteful",
          value: analytics.conversations_by_efficiency.wasteful,
          color: "bg-red-500",
          percentage:
            analytics.total_conversations > 0
              ? Math.round(
                  (analytics.conversations_by_efficiency.wasteful / analytics.total_conversations) *
                    100
                )
              : 0,
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/dashboard/conversations">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-xl font-semibold">Chat Analytics</h1>
            <p className="text-sm text-muted-foreground">
              Analyze conversation efficiency and identify abandoned chats
            </p>
          </div>
        </div>
        <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
          <SelectTrigger className="w-[200px]">
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
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="mb-4 h-16 w-16 animate-spin text-muted-foreground/50" />
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      ) : error instanceof Error ? (
        <div className="flex flex-col items-center justify-center py-16">
          <AlertCircle className="mb-4 h-16 w-16 text-destructive" />
          <h3 className="mb-2 text-lg font-semibold">Failed to load analytics</h3>
          <p className="max-w-sm text-center text-sm text-muted-foreground">{error.message}</p>
        </div>
      ) : !analytics || analytics.total_conversations === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <BarChart3 className="mb-4 h-16 w-16 text-muted-foreground/50" />
          <h3 className="mb-2 text-lg font-semibold">No conversations to analyze</h3>
          <p className="max-w-sm text-center text-sm text-muted-foreground">
            Analytics will appear here once your chat agents start handling conversations
          </p>
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Conversations</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics.total_conversations}</div>
                <p className="text-xs text-muted-foreground">
                  {analytics.total_messages.toLocaleString()} total messages
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Messages</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics.avg_messages_per_conversation}</div>
                <p className="text-xs text-muted-foreground">
                  {analytics.avg_tokens_per_conversation.toLocaleString()} tokens avg
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Est. Total Cost</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ${analytics.estimated_cost_total.toFixed(4)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {analytics.total_tokens.toLocaleString()} total tokens
                </p>
              </CardContent>
            </Card>

            <Card className="border-red-500/20">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Wasted Cost</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-500">
                  ${analytics.estimated_cost_wasted.toFixed(4)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {analytics.conversations_by_efficiency.wasteful} abandoned conversations
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Efficiency Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Efficiency Distribution
              </CardTitle>
              <CardDescription>
                Conversations rated by engagement (messages exchanged)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {chartData.map((item) => (
                  <div key={item.label} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{item.label}</span>
                      <span className="text-muted-foreground">
                        {item.value} conversations ({item.percentage}%)
                      </span>
                    </div>
                    <div className="h-3 w-full overflow-hidden rounded-full bg-secondary">
                      <div
                        className={`h-full transition-all ${item.color}`}
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 flex gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-emerald-500" />
                  <span>Efficient: 5+ messages</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-amber-500" />
                  <span>Moderate: 2-4 messages</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500" />
                  <span>Wasteful: &lt;2 messages</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Messages vs Tokens Visualization */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Coins className="h-5 w-5" />
                Messages vs Token Usage
              </CardTitle>
              <CardDescription>
                Visual representation of message count relative to token consumption
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative h-64 w-full rounded-lg border bg-muted/30 p-4">
                {/* Y-axis label */}
                <div className="absolute -left-2 top-1/2 -translate-y-1/2 -rotate-90 text-xs text-muted-foreground">
                  Token Count
                </div>

                {/* X-axis label */}
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-xs text-muted-foreground">
                  Message Count
                </div>

                {/* Plot area */}
                <div className="relative h-full w-full">
                  {analytics.efficiency_scores.slice(0, 50).map((conv) => {
                    // Normalize positions (0-100%)
                    const maxMessages = Math.max(
                      ...analytics.efficiency_scores.map((s) => s.message_count)
                    );
                    const maxTokens = Math.max(
                      ...analytics.efficiency_scores.map((s) => s.total_tokens)
                    );
                    const x = (conv.message_count / (maxMessages || 1)) * 90;
                    const y = 90 - (conv.total_tokens / (maxTokens || 1)) * 85;

                    return (
                      <div
                        key={conv.conversation_id}
                        className={`absolute h-2.5 w-2.5 rounded-full transition-all hover:scale-150 ${getEfficiencyColor(conv.efficiency_rating)}`}
                        style={{
                          left: `${x + 5}%`,
                          top: `${y}%`,
                        }}
                        title={`${conv.agent_name ?? "Unknown"}: ${conv.message_count} messages, ${conv.total_tokens.toLocaleString()} tokens`}
                      />
                    );
                  })}
                </div>
              </div>
              <p className="mt-2 text-center text-xs text-muted-foreground">
                Hover over dots for details. Points in the bottom-left are low-engagement
                conversations.
              </p>
            </CardContent>
          </Card>

          {/* Wasteful Conversations Table */}
          {wastefulConversations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-500">
                  <AlertTriangle className="h-5 w-5" />
                  Abandoned Conversations
                </CardTitle>
                <CardDescription>
                  Conversations with very few messages - potential user confusion or abandonment
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Agent</TableHead>
                      <TableHead>Messages</TableHead>
                      <TableHead>Tokens</TableHead>
                      <TableHead>Duration</TableHead>
                      <TableHead>Est. Cost</TableHead>
                      <TableHead>Rating</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {wastefulConversations.slice(0, 20).map((conv) => (
                      <TableRow key={conv.conversation_id}>
                        <TableCell className="text-sm">
                          {new Date(conv.started_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell className="font-medium">
                          {conv.agent_name ?? "Unknown"}
                        </TableCell>
                        <TableCell>{conv.message_count}</TableCell>
                        <TableCell>{conv.total_tokens.toLocaleString()}</TableCell>
                        <TableCell>{formatDuration(conv.duration_seconds)}</TableCell>
                        <TableCell>
                          $
                          {(
                            (conv.input_tokens / 1_000_000) * 0.15 +
                            (conv.output_tokens / 1_000_000) * 0.6
                          ).toFixed(4)}
                        </TableCell>
                        <TableCell>
                          <Badge variant={getEfficiencyBadgeVariant(conv.efficiency_rating)}>
                            {conv.efficiency_rating}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {wastefulConversations.length > 20 && (
                  <p className="mt-4 text-center text-sm text-muted-foreground">
                    Showing 20 of {wastefulConversations.length} abandoned conversations
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
