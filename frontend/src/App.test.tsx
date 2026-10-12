import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("FormFlow shell", () => {
  it("renders a physical-coordinate stage editor", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "FormFlow" })).toBeDefined();
    expect(screen.getByText(/16m × 10m/)).toBeDefined();
    expect(screen.getByRole("button", { name: "Generate transition" })).toBeDefined();
  });
});
