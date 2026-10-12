from fastapi import FastAPI

from app.assignment.solver import solve_assignment
from app.collision.validator import validate_transition
from app.formations.templates import generate_template
from app.metrics.calculator import calculate_metrics
from app.models.domain import (
    AssignmentRequest,
    AssignmentResponse,
    Metrics,
    Project,
    TemplateRequest,
    TemplateResponse,
    TransitionPlanRequest,
    TransitionPlanResponse,
    ValidateRequest,
    ValidationResult,
)
from app.path_planning.baseline import plan_straight_paths

app = FastAPI(title="FormFlow API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/assignments/solve", response_model=AssignmentResponse)
def assignments_solve(request: AssignmentRequest) -> AssignmentResponse:
    return solve_assignment(request)


@app.post("/formations/template", response_model=TemplateResponse)
def formation_template(request: TemplateRequest) -> TemplateResponse:
    return TemplateResponse(slots=generate_template(request))


@app.post("/transitions/plan", response_model=TransitionPlanResponse)
def transitions_plan(request: TransitionPlanRequest) -> TransitionPlanResponse:
    return plan_straight_paths(request)


@app.post("/transitions/validate", response_model=ValidationResult)
def transitions_validate(request: ValidateRequest) -> ValidationResult:
    return validate_transition(request)


@app.post("/transitions/metrics", response_model=Metrics)
def transitions_metrics(request: ValidateRequest) -> Metrics:
    validation = validate_transition(request)
    return calculate_metrics(request.paths, request.duration_seconds, validation, 0)


@app.get("/examples")
def examples() -> list[dict[str, str]]:
    return [{"id": "crossing-six", "name": "Crossing six"}]


@app.get("/examples/{example_id}")
def example(example_id: str) -> dict:
    if example_id != "crossing-six":
        return {"error": "Example not found"}
    dancers = [{"id": f"d{i}", "label": chr(64 + i), "radius": 0.3} for i in range(1, 7)]
    return {"schema_version": "1.0", "id": "crossing-six", "name": "Crossing six", "stage": {"width": 16, "depth": 10}, "dancers": dancers}


@app.post("/projects/validate", response_model=Project)
def project_validate(project: Project) -> Project:
    """Schema validation boundary for imported versioned project JSON."""
    return project
