# my_agent

An Agent Development Kit (ADK) sample that builds a travel planning assistant with non‑sequential, intent‑routed sub‑agents and a single polished final response.

## Quick start

- **[create venv]**
  - Windows PowerShell
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

- **[run web UI]** from repo root
  ```powershell
  adk web . --port 8000
  ```

- **[open]** http://127.0.0.1:8000 and select app `my_agent`.

- **[env]** Add a `GOOGLE_API_KEY` to `my_agent/.env` for Gemini API.

## App discovery

- Root agent is exported as `root_agent` in `my_agent/agent.py` and re‑exported in `my_agent/__init__.py`.
- ADK searches for `my_agent.agent.root_agent` or `my_agent/root_agent.yaml` under the agents directory.

## Architecture

See `my_agent/architecture.md` for a diagram. High‑level:

- **[root]** `root = SequentialAgent(name="RootPlanner", sub_agents=[master_agent])`
- **[master]** `master_agent = SequentialAgent(name="MasterAgent", sub_agents=[planning_loop])`
- **[planner loop]** `CheckLoopAgent` with custom `_run_async_impl()` orchestrates sub‑agents non‑sequentially based on the user query.

### Sub‑agents (tools)

- **`QueryAgent`** (`output_key="trip_params"`): parses user question into structured parameters.
- **`InformationAgent`** (`output_key="trip_info"`): flights, hotels, activities; rich, actionable sections.
- **`BudgetAgent`** (`output_key="cost_estimate"`): breakdown in INR/EUR with Low/Medium/High table and tips.
- **`ItineraryAgent`** (`output_key="itinerary"`): day‑wise plan with blocks, transit, time, costs.
- **`ValidatorAgent`** (`output_key="validation_status"`): returns `valid` or fixes with issues.
- **`PresenterAgent`** (`output_key="final_plan_draft"`): composes a comprehensive draft.
- **`PolisherAgent`** (`output_key="final_plan"`): enforces a quality rubric and emits the single visible response.

All agents are defined in `my_agent/agent.py`.

### State keys

- `trip_params`, `trip_info`, `cost_estimate`, `itinerary`, `validation_status`, `final_plan_draft`, `final_plan`.
- Keys are default‑initialized to empty strings to prevent template KeyErrors.

## Routing (non‑sequential)

Implemented in `CheckLoopAgent._run_async_impl()` within `my_agent/agent.py`:

- Always run `QueryAgent` first to produce `trip_params`.
- Determine `route` by keyword precedence:
  - `itinerary` and `budget` → `full`
  - else `itinerary` → `itinerary`
  - else `budget` → `budget`
  - else `info` → `info`
  - else default `full`
- Execute only the required agents for the chosen route, silently consuming their events.
- Produce a draft via `PresenterAgent`, then output the polished final via `PolisherAgent`.

## Single final response

- Sub‑agent events are consumed; only `PolisherAgent` output is returned to the UI.
- The loop yields an escalate event after the final message to terminate cleanly.

## Models

- Agents currently use `gemini-2.5-flash`. Update the `model=` values in `my_agent/agent.py` if your project requires different models or quotas.

## Testing

- A ready‑made test set lives in `my_agent/test.md` (25 questions):
  - Each case includes expected route, agents invoked, and reasoning based on router rules.

### Example prompts

- “What’s the estimated budget for a 5‑day trip from Bengaluru to Paris starting 20 Nov 2025?” → `budget`
- “Create a 5‑day day‑wise itinerary for Paris and validate feasibility.” → `itinerary` (+ validator)
- “Give me information about top activities in Paris for 5 days.” → `info`

## Troubleshooting

- **App name mismatch warning**: Non‑fatal. Prefer starting with `adk web . --port 8000` from repo root.
- **Missing key errors**: Keys are default‑initialized; if you change agent prompts to reference new keys, also initialize them in `_run_async_impl()`.
- **Rate limits (429)**: The loop runs minimal agents per query; if you still hit rpm limits, consider splitting models across agents or waiting 60 seconds between runs.

## Repository structure (relevant)

- `my_agent/agent.py` — agents, router, and root.
- `my_agent/__init__.py` — exports `root_agent`.
- `my_agent/architecture.md` — architecture diagram and rationale.
- `my_agent/test.md` — test questions table.
