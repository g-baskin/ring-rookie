"use client";

import type { ControllerRenderProps, FieldPath, FieldValues } from "react-hook-form";

import {
  FormControl,
  FormDescription,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";

export const DEFAULT_PROMPT_CHARACTER_TARGET = 5000;
export const MIN_PROMPT_CHARACTER_TARGET = 1000;
export const MAX_PROMPT_CHARACTER_TARGET = 20000;

export function clampPromptCharacterTarget(value: number): number {
  if (!Number.isFinite(value)) return DEFAULT_PROMPT_CHARACTER_TARGET;
  return Math.min(
    MAX_PROMPT_CHARACTER_TARGET,
    Math.max(MIN_PROMPT_CHARACTER_TARGET, Math.round(value))
  );
}

export function isPromptOverTarget(characterCount: number, target: number): boolean {
  return characterCount > target;
}

type PromptCharacterTargetFieldProps<
  TFieldValues extends FieldValues,
  TName extends FieldPath<TFieldValues>,
> = {
  field: ControllerRenderProps<TFieldValues, TName>;
};

export function PromptCharacterTargetField<
  TFieldValues extends FieldValues,
  TName extends FieldPath<TFieldValues>,
>({ field }: PromptCharacterTargetFieldProps<TFieldValues, TName>) {
  const value = Number(field.value ?? DEFAULT_PROMPT_CHARACTER_TARGET);

  return (
    <FormItem>
      <FormLabel htmlFor="system-prompt-character-target">
        Recommended prompt-length target
      </FormLabel>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <FormControl>
          <Input
            id="system-prompt-character-target"
            aria-label="Recommended prompt-length target value"
            type="number"
            min={MIN_PROMPT_CHARACTER_TARGET}
            max={MAX_PROMPT_CHARACTER_TARGET}
            step={1}
            value={value}
            onChange={(event) => field.onChange(event.target.valueAsNumber)}
            onBlur={(event) => {
              field.onChange(clampPromptCharacterTarget(Number(event.target.value)));
              field.onBlur();
            }}
            className="w-full sm:w-32"
          />
        </FormControl>
        <Slider
          aria-label="Recommended prompt-length target slider"
          aria-valuemin={MIN_PROMPT_CHARACTER_TARGET}
          aria-valuemax={MAX_PROMPT_CHARACTER_TARGET}
          aria-valuenow={value}
          min={MIN_PROMPT_CHARACTER_TARGET}
          max={MAX_PROMPT_CHARACTER_TARGET}
          step={100}
          value={[value]}
          onValueChange={(nextValue) => field.onChange(nextValue[0])}
          className="flex-1"
        />
      </div>
      <FormDescription>
        A recommended system-prompt length, not the model output max tokens.
      </FormDescription>
      <FormMessage />
    </FormItem>
  );
}
