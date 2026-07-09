# AutoMate

AutoMate is an in-vehicle AI agent MVP that classifies Korean driver utterances, selects vehicle tools, applies safety policies, and logs execution results for evaluation.

## Stack

- **Backend**: FastAPI, rule-based / hybrid NLU, Vehicle Capability Catalog, Tool Registry, Safety Guard
- **Frontend**: React + TypeScript console for agent testing, logs, evaluation, and scenario runner

## Quick Start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

## Road Context Awareness

AutoMate can handle road-context queries such as current speed limit, road name, school-zone status, and speeding status. This feature demonstrates that the agent considers not only in-vehicle state but also driving-road context for safer responses.

Supported capabilities:

- **Current road speed limit** — compares `speed` with `speed_limit` from vehicle/road context
- **Speeding status** — answers whether the driver is within the limit and includes safety guidance when over
- **Road name** — reports the current road name when available
- **School zone** — checks `is_school_zone` and recommends slowing down when needed
- **Low-risk while driving** — road context checks are allowed during driving (`allowed_while_driving: true`)

Example utterances:

- `지금 제한속도 몇이야?`
- `나 과속 중이야?`
- `속도 괜찮아?`
- `지금 도로 이름 뭐야?`
- `여기 어린이 보호구역이야?`

Intent: `CHECK_ROAD_CONTEXT`  
Tool: `checkRoadContext`

Vehicle context fields used:

- `road_name`, `road_type`, `speed_limit`, `is_school_zone`, `navigation_active`

When `speed_limit` is unavailable, the tool returns a failure response and the agent explains that road data is not connected yet.

## Architecture Notes

- **Vehicle Capability Catalog** (`backend/app/data/vehicle-capabilities.json`) defines intents, tools, slots, safety policy, and response templates.
- **CapabilityService** matches utterances and extracts slots.
- **Tool Registry** executes validated tools such as `setClimate`, `checkVehicleStatus`, and `checkRoadContext`.
- **Scenario Runner** validates intent, tool, and safety accuracy against `backend/app/data/test-scenarios.json`.
