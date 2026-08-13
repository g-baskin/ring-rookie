"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { createLesson, type Lesson, updateLesson } from "@/lib/api/lessons";

interface LessonDialogProps {
  agentId: string;
  workspaceId?: string | null;
  sourceCallId: string | null;
  lesson?: Lesson | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
}

export function LessonDialog({
  agentId,
  workspaceId,
  sourceCallId,
  lesson,
  open,
  onOpenChange,
  onSaved,
}: LessonDialogProps) {
  const [title, setTitle] = useState("");
  const [observation, setObservation] = useState("");
  const [recommendedAction, setRecommendedAction] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    setTitle(lesson?.title ?? "");
    setObservation(lesson?.observation ?? "");
    setRecommendedAction(lesson?.recommended_action ?? "");
  }, [lesson, open]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!sourceCallId && !lesson) return;
    setSaving(true);
    try {
      if (lesson) {
        await updateLesson(
          agentId,
          lesson.id,
          { title, observation, recommended_action: recommendedAction },
          workspaceId
        );
      } else if (sourceCallId) {
        await createLesson(
          agentId,
          {
            source_call_id: sourceCallId,
            title,
            observation,
            recommended_action: recommendedAction,
          },
          workspaceId
        );
      }
      toast.success(lesson ? "Lesson updated" : "Lesson saved");
      onOpenChange(false);
      onSaved();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to save lesson");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <form
          onSubmit={(event) => {
            void handleSubmit(event);
          }}
          className="space-y-4"
        >
          <DialogHeader>
            <DialogTitle>{lesson ? "Edit lesson" : "Save lesson"}</DialogTitle>
            <DialogDescription>
              Capture the minimum summary needed to improve this agent. Do not paste names, phone
              numbers, addresses, or unnecessary transcript excerpts.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="lesson-title">Title</Label>
            <Input
              id="lesson-title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              maxLength={200}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="lesson-observation">What went wrong or what did you learn?</Label>
            <Textarea
              id="lesson-observation"
              value={observation}
              onChange={(event) => setObservation(event.target.value)}
              maxLength={5000}
              rows={5}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="lesson-action">Recommended prompt or action change</Label>
            <Textarea
              id="lesson-action"
              value={recommendedAction}
              onChange={(event) => setRecommendedAction(event.target.value)}
              maxLength={5000}
              rows={4}
              required
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving || (!sourceCallId && !lesson)}>
              {saving ? "Saving…" : lesson ? "Update lesson" : "Save lesson"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
