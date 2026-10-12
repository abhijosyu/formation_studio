export type Point = { x: number; y: number };
export type Dancer = { id: string; label: string; radius: number };
export type TargetSlot = { id: string; position: Point };
export type AssignmentStrategy = "greedy_nearest" | "minimum_total_distance" | "movement_aware";
export type Conflict = { kind: string; time_seconds: number; location: Point; dancer_ids: string[]; detail: string };
export type Metrics = { total_distance: number; max_individual_distance: number; mean_individual_distance: number; collision_count: number; minimum_separation: number; path_crossings: number; direction_changes: number; duration_seconds: number; planning_time_ms: number; validation_status: string };
export type AssignmentResponse = { strategy: AssignmentStrategy; assignments: { dancer_id: string; target_id: string; cost: number }[]; total_cost: number };
export type TransitionPlan = { assignment: AssignmentResponse; paths: { dancer_id: string; points: Point[]; interpolation: "smoothstep" }[]; duration_seconds: number; validation: { status: string; conflicts: Conflict[]; minimum_separation: number; samples_checked: number }; metrics: Metrics; status: "valid" | "conflicts_detected" | "no_valid_transition_found" | "validation_incomplete"; note: string };
