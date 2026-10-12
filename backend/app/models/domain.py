from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

Positive = Annotated[float, Field(gt=0)]
Coordinate = Annotated[float, Field(ge=-10_000, le=10_000)]


class Point(BaseModel):
    """Physical stage coordinate in metres; origin is centre stage."""
    x: Coordinate
    y: Coordinate


class Stage(BaseModel):
    width: Positive = Field(description="metres")
    depth: Positive = Field(description="metres")


class CircleObstacle(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    center: Point
    radius: Positive


class Dancer(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=64)
    radius: Positive = 0.3


class TargetSlot(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    position: Point


class Formation(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=100)
    slots: list[TargetSlot] = Field(default_factory=list, max_length=48)

    @model_validator(mode="after")
    def unique_slot_ids(self) -> Formation:
        if len({slot.id for slot in self.slots}) != len(self.slots):
            raise ValueError("Formation slot IDs must be unique")
        return self


class AssignmentStrategy(StrEnum):
    GREEDY = "greedy_nearest"
    MINIMUM_DISTANCE = "minimum_total_distance"
    MOVEMENT_AWARE = "movement_aware"


class AssignmentRequest(BaseModel):
    dancers: list[Dancer] = Field(min_length=1, max_length=48)
    start_positions: dict[str, Point]
    targets: list[TargetSlot] = Field(min_length=1, max_length=48)
    strategy: AssignmentStrategy = AssignmentStrategy.MINIMUM_DISTANCE

    @model_validator(mode="after")
    def valid_assignment_input(self) -> AssignmentRequest:
        ids = [dancer.id for dancer in self.dancers]
        if len(set(ids)) != len(ids):
            raise ValueError("Dancer IDs must be unique")
        if set(self.start_positions) != set(ids):
            raise ValueError("start_positions must contain exactly one position for every dancer")
        if len(self.targets) != len(self.dancers):
            raise ValueError("MVP requires an equal number of dancers and target slots.")
        if len({target.id for target in self.targets}) != len(self.targets):
            raise ValueError("Target slot IDs must be unique")
        return self


class Assignment(BaseModel):
    dancer_id: str
    target_id: str
    cost: float = Field(ge=0)


class AssignmentResponse(BaseModel):
    strategy: AssignmentStrategy
    assignments: list[Assignment]
    total_cost: float = Field(ge=0)


class TemplateKind(StrEnum):
    LINE = "line"
    DIAGONAL = "diagonal"
    V = "v"
    CIRCLE = "circle"
    GRID = "grid"
    STAGGERED_ROWS = "staggered_rows"


class TemplateRequest(BaseModel):
    kind: TemplateKind
    count: int = Field(ge=1, le=48)
    center: Point = Point(x=0, y=0)
    row_spacing: Positive = 1.0
    column_spacing: Positive = 1.0
    rotation_degrees: float = Field(default=0, ge=-360, le=360)
    mirrored: bool = False


class TemplateResponse(BaseModel):
    slots: list[TargetSlot]


class Path(BaseModel):
    dancer_id: str
    points: list[Point] = Field(min_length=2, max_length=16)
    interpolation: Literal["smoothstep"] = "smoothstep"


class PlannerConfig(BaseModel):
    safety_margin: float = Field(default=0.1, ge=0, le=2)
    sample_count: int = Field(default=120, ge=20, le=1000)
    advanced: bool = True
    max_waypoint_attempts: int = Field(default=12, ge=0, le=48)
    distance_weight: float = Field(default=1, ge=0, le=100)
    collision_weight: float = Field(default=25, ge=0, le=1000)
    boundary_weight: float = Field(default=25, ge=0, le=1000)


class Conflict(BaseModel):
    kind: Literal["dancer_collision", "boundary", "obstacle", "initial_overlap", "final_overlap"]
    time_seconds: float = Field(ge=0)
    location: Point
    dancer_ids: list[str] = Field(min_length=1, max_length=2)
    detail: str


class ValidationResult(BaseModel):
    status: Literal["valid", "conflicts_detected", "validation_incomplete"]
    conflicts: list[Conflict]
    minimum_separation: float = Field(ge=0)
    samples_checked: int = Field(ge=0)


class Metrics(BaseModel):
    total_distance: float
    max_individual_distance: float
    mean_individual_distance: float
    collision_count: int
    minimum_separation: float
    path_crossings: int
    direction_changes: int
    duration_seconds: float
    planning_time_ms: float
    validation_status: str


class TransitionPlanRequest(BaseModel):
    assignment_request: AssignmentRequest
    stage: Stage = Stage(width=16, depth=10)
    obstacles: list[CircleObstacle] = Field(default_factory=list, max_length=24)
    duration_seconds: Positive = Field(default=4, le=120)
    config: PlannerConfig = Field(default_factory=PlannerConfig)


class TransitionPlanResponse(BaseModel):
    assignment: AssignmentResponse
    paths: list[Path]
    duration_seconds: float
    validation: ValidationResult
    metrics: Metrics
    status: Literal["valid", "conflicts_detected", "no_valid_transition_found", "validation_incomplete"]
    note: str


class ValidateRequest(BaseModel):
    dancers: list[Dancer] = Field(min_length=1, max_length=48)
    paths: list[Path] = Field(min_length=1, max_length=48)
    stage: Stage
    obstacles: list[CircleObstacle] = Field(default_factory=list, max_length=24)
    duration_seconds: Positive = Field(le=120)
    config: PlannerConfig = Field(default_factory=PlannerConfig)


class Project(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    stage: Stage
    dancers: list[Dancer]
    formations: list[Formation]
    transitions: list[TransitionPlanResponse] = Field(default_factory=list)
    planner_config: PlannerConfig = Field(default_factory=PlannerConfig)
