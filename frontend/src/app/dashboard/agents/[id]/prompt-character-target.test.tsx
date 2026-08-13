import { fireEvent, render, screen } from "@testing-library/react";
import { useForm } from "react-hook-form";
import { describe, expect, it } from "vitest";

import { Form, FormField } from "@/components/ui/form";

import {
  clampPromptCharacterTarget,
  isPromptOverTarget,
  PromptCharacterTargetField,
} from "./prompt-character-target";

function Harness() {
  const form = useForm({ defaultValues: { target: 5000 } });
  return (
    <Form {...form}>
      <FormField
        control={form.control}
        name="target"
        render={({ field }) => <PromptCharacterTargetField field={field} />}
      />
    </Form>
  );
}

describe("PromptCharacterTargetField", () => {
  it("defaults to 5,000 and synchronizes number and slider changes", () => {
    render(<Harness />);

    const input = screen.getByLabelText("Recommended prompt-length target value");
    const slider = screen.getByLabelText("Recommended prompt-length target slider");
    expect(input).toHaveValue(5000);
    expect(slider).toHaveAttribute("aria-valuenow", "5000");

    fireEvent.change(input, { target: { value: "6500" } });
    expect(slider).toHaveAttribute("aria-valuenow", "6500");

    fireEvent.keyDown(slider, { key: "ArrowRight" });
    expect(input).toHaveValue(6600);
  });

  it("clamps numeric input on blur", () => {
    render(<Harness />);
    const input = screen.getByLabelText("Recommended prompt-length target value");

    fireEvent.change(input, { target: { value: "999999" } });
    fireEvent.blur(input);

    expect(input).toHaveValue(20000);
  });
});

describe("prompt target helpers", () => {
  it("warns only after the configured boundary", () => {
    expect(isPromptOverTarget(5000, 5000)).toBe(false);
    expect(isPromptOverTarget(5001, 5000)).toBe(true);
  });

  it("uses 5,000 for invalid values", () => {
    expect(clampPromptCharacterTarget(Number.NaN)).toBe(5000);
  });
});
