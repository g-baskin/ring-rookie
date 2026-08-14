"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, Loader2, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { deleteLesson, downloadLessons, fetchLessons, type Lesson } from "@/lib/api/lessons";

interface LessonsPanelProps {
  agentId: string;
  workspaceId?: string | null;
  onEdit: (lesson: Lesson) => void;
}

export function LessonsPanel({ agentId, workspaceId, onEdit }: LessonsPanelProps) {
  const queryClient = useQueryClient();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const queryKey = ["lessons", agentId, workspaceId ?? null];
  const { data: lessons = [], isLoading } = useQuery({
    queryKey,
    queryFn: () => fetchLessons(agentId, workspaceId),
    enabled: Boolean(agentId),
  });

  async function removeLesson(lessonId: string) {
    try {
      await deleteLesson(agentId, lessonId, workspaceId);
      setSelectedIds((current) => current.filter((id) => id !== lessonId));
      await queryClient.invalidateQueries({ queryKey });
      toast.success("Lesson deleted");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to delete lesson");
    }
  }

  async function exportLessons(format: "csv" | "json") {
    try {
      await downloadLessons(agentId, format, workspaceId, selectedIds);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to export lessons");
    }
  }

  return (
    <section className="space-y-3" aria-labelledby="lessons-heading">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h2 id="lessons-heading" className="text-sm font-medium">
            Lessons learned
          </h2>
          {selectedIds.length > 0 && (
            <p className="text-[10px] text-muted-foreground">
              Exporting {selectedIds.length} selected
            </p>
          )}
        </div>
        <div className="flex gap-1">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={lessons.length === 0}
            onClick={() => void exportLessons("csv")}
          >
            <Download className="mr-1 h-3 w-3" /> CSV
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={lessons.length === 0}
            onClick={() => void exportLessons("json")}
          >
            <Download className="mr-1 h-3 w-3" /> JSON
          </Button>
        </div>
      </div>
      {isLoading ? (
        <Loader2
          className="h-4 w-4 animate-spin text-muted-foreground"
          aria-label="Loading lessons"
        />
      ) : lessons.length === 0 ? (
        <p className="text-xs text-muted-foreground">No lessons saved for this agent.</p>
      ) : (
        <ul className="max-h-56 space-y-2 overflow-y-auto">
          {lessons.map((lesson) => (
            <li key={lesson.id} className="rounded-md border bg-background p-3 text-xs">
              <div className="flex items-start gap-2">
                <Checkbox
                  checked={selectedIds.includes(lesson.id)}
                  aria-label={`Select lesson ${lesson.title}`}
                  onCheckedChange={(checked) =>
                    setSelectedIds((current) =>
                      checked ? [...current, lesson.id] : current.filter((id) => id !== lesson.id)
                    )
                  }
                />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{lesson.title}</p>
                  <p className="mt-1 line-clamp-2 text-muted-foreground">{lesson.observation}</p>
                  <p className="mt-1 line-clamp-2">Change: {lesson.recommended_action}</p>
                  <time className="mt-1 block text-[10px] text-muted-foreground">
                    {new Date(lesson.created_at).toLocaleString()}
                  </time>
                </div>
                <div className="flex shrink-0">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    aria-label={`Edit lesson ${lesson.title}`}
                    onClick={() => onEdit(lesson)}
                  >
                    <Pencil className="h-3 w-3" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    aria-label={`Delete lesson ${lesson.title}`}
                    onClick={() => void removeLesson(lesson.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
