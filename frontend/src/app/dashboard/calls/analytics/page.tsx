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
  Clock,
  DollarSign,
  AlertTriangle,
  TrendingUp,
  ArrowLeft,
  Loader2,
  AlertCircle,
  PhoneCall,
  MessageSquare,
  Lightbulb,
  Settings,
  ExternalLink,
} from "lucide-react";
import { getCallAnalytics } from "@/lib/api/calls";
import { api } from "@/lib/api";

interface Agent {
  id: string;
  name: string;
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hours > 0) return `${hours}h ${mins}m`;
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

export default function CallAnalyticsPage() {
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
    queryKey: ["call-analytics", selectedAgentId],
    queryFn: () =>
      getCallAnalytics({
        agent_id: selectedAgentId !== "all" ? selectedAgentId : undefined,
      }),
  });

  // Get wasteful calls for the table
  const wastefulCalls =
    analytics?.efficiency_scores.filter((s) => s.efficiency_rating === "wasteful") ?? [];

  // Calculate bar chart data
  const chartData = analytics
    ? [
        {
          label: "Efficient",
          value: analytics.calls_by_efficiency.efficient,
          color: "bg-emerald-500",
          percentage:
            analytics.total_calls > 0
              ? Math.round((analytics.calls_by_efficiency.efficient / analytics.total_calls) * 100)
              : 0,
        },
        {
          label: "Moderate",
          value: analytics.calls_by_efficiency.moderate,
          color: "bg-amber-500",
          percentage:
            analytics.total_calls > 0
              ? Math.round((analytics.calls_by_efficiency.moderate / analytics.total_calls) * 100)
              : 0,
        },
        {
          label: "Wasteful",
          value: analytics.calls_by_efficiency.wasteful,
          color: "bg-red-500",
          percentage:
            analytics.total_calls > 0
              ? Math.round((analytics.calls_by_efficiency.wasteful / analytics.total_calls) * 100)
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
            <Link href="/dashboard/calls">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-xl font-semibold">Call Analytics</h1>
            <p className="text-sm text-muted-foreground">
              Analyze call efficiency and identify cost waste
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
      ) : !analytics || analytics.total_calls === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <BarChart3 className="mb-4 h-16 w-16 text-muted-foreground/50" />
          <h3 className="mb-2 text-lg font-semibold">No calls to analyze</h3>
          <p className="max-w-sm text-center text-sm text-muted-foreground">
            Analytics will appear here once your voice agents start handling calls
          </p>
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Calls</CardTitle>
                <PhoneCall className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics.total_calls}</div>
                <p className="text-xs text-muted-foreground">
                  {formatDuration(analytics.total_duration_seconds)} total duration
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Duration</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatDuration(Math.round(analytics.avg_duration_seconds))}
                </div>
                <p className="text-xs text-muted-foreground">
                  {analytics.avg_words_per_minute.toFixed(0)} words/min avg
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
                  ${analytics.estimated_cost_total.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground">Based on ~$0.15/min</p>
              </CardContent>
            </Card>

            <Card className="border-red-500/20">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Wasted Cost</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-500">
                  ${analytics.estimated_cost_wasted.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {analytics.calls_by_efficiency.wasteful} wasteful calls
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
                Calls rated by content density (words per minute of call time)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {chartData.map((item) => (
                  <div key={item.label} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{item.label}</span>
                      <span className="text-muted-foreground">
                        {item.value} calls ({item.percentage}%)
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
                  <span>Efficient: 30+ WPM</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-amber-500" />
                  <span>Moderate: 15-30 WPM</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500" />
                  <span>Wasteful: &lt;15 WPM</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Duration vs Content Visualization */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Duration vs Content
              </CardTitle>
              <CardDescription>
                Visual representation of call duration relative to word count
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative h-64 w-full rounded-lg border bg-muted/30 p-4">
                {/* Y-axis label */}
                <div className="absolute -left-2 top-1/2 -translate-y-1/2 -rotate-90 text-xs text-muted-foreground">
                  Word Count
                </div>

                {/* X-axis label */}
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-xs text-muted-foreground">
                  Duration (seconds)
                </div>

                {/* Plot area */}
                <div className="relative h-full w-full">
                  {analytics.efficiency_scores.slice(0, 50).map((call) => {
                    // Normalize positions (0-100%)
                    const maxDuration = Math.max(
                      ...analytics.efficiency_scores.map((s) => s.duration_seconds)
                    );
                    const maxWords = Math.max(
                      ...analytics.efficiency_scores.map((s) => s.word_count)
                    );
                    const x = (call.duration_seconds / (maxDuration ?? 1)) * 90;
                    const y = 90 - (call.word_count / (maxWords ?? 1)) * 85;

                    return (
                      <div
                        key={call.call_id}
                        className={`absolute h-2.5 w-2.5 rounded-full transition-all hover:scale-150 ${getEfficiencyColor(call.efficiency_rating)}`}
                        style={{
                          left: `${x + 5}%`,
                          top: `${y}%`,
                        }}
                        title={`${call.agent_name ?? "Unknown"}: ${formatDuration(call.duration_seconds)}, ${call.word_count} words, ${call.words_per_minute} WPM`}
                      />
                    );
                  })}

                  {/* Reference line for 30 WPM (efficient threshold) */}
                  <div className="pointer-events-none absolute inset-0">
                    <svg className="h-full w-full" preserveAspectRatio="none">
                      <line
                        x1="5%"
                        y1="90%"
                        x2="95%"
                        y2="5%"
                        stroke="currentColor"
                        strokeDasharray="4"
                        strokeWidth="1"
                        className="text-emerald-500/30"
                      />
                    </svg>
                  </div>
                </div>
              </div>
              <p className="mt-2 text-center text-xs text-muted-foreground">
                Hover over dots for details. Points below the dashed line are less efficient.
              </p>
            </CardContent>
          </Card>

          {/* Wasteful Calls Table */}
          {wastefulCalls.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-500">
                  <AlertTriangle className="h-5 w-5" />
                  Wasteful Calls
                </CardTitle>
                <CardDescription>
                  Calls with low content density (&lt;15 words per minute) - potential cost waste
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Agent</TableHead>
                      <TableHead>Duration</TableHead>
                      <TableHead>Words</TableHead>
                      <TableHead>WPM</TableHead>
                      <TableHead>Est. Cost</TableHead>
                      <TableHead>Rating</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {wastefulCalls.slice(0, 20).map((call) => (
                      <TableRow key={call.call_id}>
                        <TableCell className="text-sm">
                          {new Date(call.started_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell className="font-medium">
                          {call.agent_name ?? "Unknown"}
                        </TableCell>
                        <TableCell>{formatDuration(call.duration_seconds)}</TableCell>
                        <TableCell>{call.word_count}</TableCell>
                        <TableCell>{call.words_per_minute.toFixed(1)}</TableCell>
                        <TableCell>${((call.duration_seconds / 60) * 0.15).toFixed(2)}</TableCell>
                        <TableCell>
                          <Badge variant={getEfficiencyBadgeVariant(call.efficiency_rating)}>
                            {call.efficiency_rating}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {wastefulCalls.length > 20 && (
                  <p className="mt-4 text-center text-sm text-muted-foreground">
                    Showing 20 of {wastefulCalls.length} wasteful calls
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Suggestions to Reduce Wasteful Calls */}
          {wastefulCalls.length > 0 && (
            <Card className="border-amber-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-amber-500">
                  <Lightbulb className="h-5 w-5" />
                  Suggestions to Reduce Wasteful Calls
                </CardTitle>
                <CardDescription>
                  Settings changes that can improve call efficiency and reduce costs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Initial Greeting Suggestion */}
                <div className="rounded-lg border bg-muted/30 p-4">
                  <div className="flex items-start gap-3">
                    <Settings className="mt-0.5 h-5 w-5 text-amber-500" />
                    <div className="flex-1">
                      <h4 className="font-medium">Enable Initial Greeting</h4>
                      <p className="mt-1 text-sm text-muted-foreground">
                        If your agent waits silently for the caller to speak first, callers may hang
                        up thinking the call failed. Set an{" "}
                        <span className="font-medium text-foreground">Initial Greeting</span> so the
                        agent speaks immediately when the call connects.
                      </p>
                      <p className="mt-2 text-sm">
                        <span className="text-muted-foreground">Location:</span>{" "}
                        <span className="font-medium">
                          Agent Settings → AI Model tab → Initial Greeting
                        </span>
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Example: &quot;Hello! Thank you for calling. How can I help you today?&quot;
                      </p>
                    </div>
                  </div>
                </div>

                {/* Turn Detection Suggestion */}
                <div className="rounded-lg border bg-muted/30 p-4">
                  <div className="flex items-start gap-3">
                    <Settings className="mt-0.5 h-5 w-5 text-amber-500" />
                    <div className="flex-1">
                      <h4 className="font-medium">Optimize Turn Detection</h4>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Long silences during calls often indicate the agent is waiting too long to
                        respond. Reduce the{" "}
                        <span className="font-medium text-foreground">Silence Duration</span>{" "}
                        setting to make the agent more responsive.
                      </p>
                      <p className="mt-2 text-sm">
                        <span className="text-muted-foreground">Location:</span>{" "}
                        <span className="font-medium">
                          Agent Settings → Advanced tab → Turn Detection
                        </span>
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Default: 500ms. Try reducing to 300-400ms for faster responses.
                      </p>
                    </div>
                  </div>
                </div>

                {/* System Prompt Suggestion */}
                <div className="rounded-lg border bg-muted/30 p-4">
                  <div className="flex items-start gap-3">
                    <Settings className="mt-0.5 h-5 w-5 text-amber-500" />
                    <div className="flex-1">
                      <h4 className="font-medium">Improve System Prompt</h4>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Callers may hang up if the agent seems confused or takes too long to help.
                        Update your{" "}
                        <span className="font-medium text-foreground">System Prompt</span> to be
                        more direct and provide clear guidance on common questions.
                      </p>
                      <p className="mt-2 text-sm">
                        <span className="text-muted-foreground">Location:</span>{" "}
                        <span className="font-medium">
                          Agent Settings → AI Model tab → System Prompt
                        </span>
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Tip: Include specific instructions for handling common scenarios quickly.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Temperature Suggestion */}
                <div className="rounded-lg border bg-muted/30 p-4">
                  <div className="flex items-start gap-3">
                    <Settings className="mt-0.5 h-5 w-5 text-amber-500" />
                    <div className="flex-1">
                      <h4 className="font-medium">Lower Temperature for Consistency</h4>
                      <p className="mt-1 text-sm text-muted-foreground">
                        High temperature values make responses more creative but less predictable.
                        For business calls, lower the{" "}
                        <span className="font-medium text-foreground">Temperature</span> to make
                        responses more focused and consistent.
                      </p>
                      <p className="mt-2 text-sm">
                        <span className="text-muted-foreground">Location:</span>{" "}
                        <span className="font-medium">
                          Agent Settings → AI Model tab → Temperature
                        </span>
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Default: 0.7. Try 0.3-0.5 for more focused responses.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Link to Agent Settings */}
                <div className="flex justify-center pt-2">
                  <Button variant="outline" asChild>
                    <Link href="/dashboard/agents">
                      <Settings className="mr-2 h-4 w-4" />
                      Go to Agent Settings
                      <ExternalLink className="ml-2 h-3 w-3" />
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
