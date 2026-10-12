import type { AssignmentStrategy, Dancer, Point, TargetSlot, TransitionPlan } from "../types/domain";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function planTransition(input: {
  dancers: Dancer[];
  starts: Record<string, Point>;
  targets: TargetSlot[];
  strategy: AssignmentStrategy;
  duration: number;
}): Promise<TransitionPlan> {
  const response = await fetch(`${API_URL}/transitions/plan`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      assignment_request: {
        dancers: input.dancers,
        start_positions: input.starts,
        targets: input.targets,
        strategy: input.strategy,
      },
      duration_seconds: input.duration,
      stage: { width: 16, depth: 10 },
      config: { advanced: true, safety_margin: 0.1, sample_count: 120 },
    }),
  });
  if (!response.ok) throw new Error((await response.json()).detail ?? "Unable to plan transition");
  return response.json() as Promise<TransitionPlan>;
}
