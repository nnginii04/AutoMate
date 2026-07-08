# AutoMate Test Scenarios

Integration test scenarios for the in-vehicle AI agent pipeline (NLU → Safety → Tool simulation).

## Source of truth

Scenario definitions live in [`app/data/test-scenarios.json`](../app/data/test-scenarios.json). The backend loads this file at runtime.

Each scenario includes:

| Field | Description |
|-------|-------------|
| `id` | Unique scenario identifier |
| `user_input` | Driver utterance |
| `vehicle_state_overrides` | Partial vehicle state for context |
| `expected_intent` | Expected classified intent |
| `expected_tool` | Expected simulated tool name (if any) |
| `expected_result` | Expected outcome flags (`success`, `safety_blocked`, `fallback`, `requires_clarification`) |
| `tags` | Labels for filtering (`safety`, `climate`, etc.) |

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/scenarios` | List all scenarios |
| `GET` | `/api/scenarios/{id}` | Get one scenario |
| `POST` | `/api/scenarios/run/{id}` | Run a single scenario |
| `POST` | `/api/scenarios/run-all` | Run all scenarios and return accuracy summary |
| `POST` | `/api/scenarios/{id}/run` | Legacy alias for single run |

## Accuracy metrics

- **Intent Accuracy** — share of scenarios with `expected_intent` that matched
- **Tool Accuracy** — share of scenarios with `expected_tool` that matched
- **Safety Accuracy** — share of safety-tagged scenarios whose `expected_result` safety flags matched

Results are persisted in `scenario_run_logs` for audit and dashboard display.
