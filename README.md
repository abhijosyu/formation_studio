# FormFlow

FormFlow plans a dance-team formation transition using physical stage coordinates, then animates the exact paths its validator evaluates.

## Run

```bash
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]' && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

`docker compose up --build` runs both services. Test everything with `pytest backend/tests`, `ruff check backend/app backend/tests`, and, in `frontend`, `npm test && npm run build && npm run lint`.

## Delivered capabilities

- SVG stage editor with metre grid, draggable dancers, target overlays, path trails, conflict markers, playback, pause/restart, and scrubbing.
- Deterministic templates: line, diagonal, V, circle, grid, and staggered rows, with mirroring/rotation.
- Greedy, Hungarian global-minimum-distance, and a movement-aware heuristic assignment. The latter adds a predicted-route-crossing penalty; it is not a global congestion solution.
- Shared smoothstep evaluator for animation and validation. Paths support editable waypoint sequences through the typed API.
- Temporal sampled collision, endpoint overlap, stage-boundary, and circle-obstacle checks. Results include time and approximate location.
- Bounded waypoint planner: on a direct-path conflict, it tries deterministic perpendicular midpoints and retains an improvement. It returns `valid`, `conflicts_detected`, or `no_valid_transition_found`; it never labels an unchecked route safe.
- Metrics: travel distances, separation, conflict count, geometric route crossings, direction changes, duration, and planning time.
- Browser local save plus versioned JSON import/export. `POST /projects/validate` validates imports server-side.
- Docker setup, CI, and a reproducible benchmark script.

## API

`GET /health`, `POST /formations/template`, `POST /assignments/solve`, `POST /transitions/plan`, `POST /transitions/validate`, `POST /transitions/metrics`, `GET /examples`, `GET /examples/{id}`, and `POST /projects/validate` all use Pydantic contracts.

Coordinates are metres with origin at centre stage. MVP requires equal dancer and slot counts. There are no accounts, databases, or external services.

## Validation and planner limitations

Validation samples 121 evenly spaced times by default, using smoothstep timing. It can miss a conflict that occurs wholly between samples; increase `sample_count` for stricter (and slower) checking. Circular dancers and circular static obstacles are supported; non-circular restricted areas are not yet supported.

Waypoint planning is a bounded local repair, not an optimal or complete multi-agent planner. If it cannot improve a conflict, it reports the remaining conflicts. The collision and boundary weights are reserved configuration fields for a later continuous optimizer; hard validation is not traded away for distance.

## Benchmark

Run `cd backend && PYTHONPATH=. .venv/bin/python benchmarks/run.py`. The deterministic grid benchmark (Python 3.14.4, seed `deterministic-grid-v1`, one run per strategy) produced the following on this machine:

| dancers | strategy | distance (m) | conflicts | result |
| ---: | --- | ---: | ---: | --- |
| 4 | greedy / minimum / movement-aware | 33.941 | 0 | valid |
| 8 | greedy | 58.543 | 0 | valid |
| 8 | minimum / movement-aware | 53.283 | 0 | valid |
| 16 | greedy | 75.375 | 0 | valid |
| 16 | minimum / movement-aware | 73.155 | 43 | no valid transition found |
| 24 | greedy | 60.000 | 0 | valid |
| 24 | minimum / movement-aware | 60.000 | 179 | no valid transition found |

The script records all outcomes rather than excluding infeasible cases. Add scenario families (circle/line, random fixed seed, and obstacles) as benchmark cases before comparing algorithm changes.
