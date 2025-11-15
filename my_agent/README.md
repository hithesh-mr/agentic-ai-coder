# my_agent

`my_agent` is an Agent Development Kit (ADK) sample app that implements a **travel planning assistant** built from multiple intent‑routed sub‑agents. It produces a single, polished Markdown response that can include trip info, a budget estimate, and a day‑by‑day itinerary.

---

## Features

- Multi‑agent travel planner using Google ADK.
- Intent‑based routing (info / budget / itinerary / full) with minimal required agents per query.
- Single final response, composed and polished from intermediate agent outputs.
- Ready‑made test set with ~25 example queries and expected routing behavior.

---

## Quick start

From the repository root (`agentic-ai-code`):

1. **Create and activate a virtual environment** (Windows PowerShell):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   - Add a `GOOGLE_API_KEY` to `my_agent/.env` for Gemini access:
     ```text
     GOOGLE_API_KEY=your-key-here
     ```

3. **Run the ADK web UI** from the repo root:
   ```powershell
   adk web . --port 8000
   ```

4. **Open the app** in a browser:
   - Visit `http://127.0.0.1:8000`.
   - Select the `my_agent` application.

---

## ADK app discovery

- The root agent is exported as `root_agent` in `my_agent/agent.py` and re‑exported in `my_agent/__init__.py`.
- ADK discovers this app by looking for `my_agent.agent.root_agent` (or `my_agent/root_agent.yaml`) under the agents directory.

---

## Architecture

See `my_agent/architecture.md` for a mermaid diagram and more detail. At a high level:

- **Root planner**:  
  `root = SequentialAgent(name="RootPlanner", sub_agents=[master_agent])`
- **Master agent**:  
  `master_agent = SequentialAgent(name="MasterAgent", sub_agents=[planning_loop])`
- **Planning loop**:  
  `CheckLoopAgent` (a `LoopAgent` subclass) with a custom `_run_async_impl()` that orchestrates sub‑agents **non‑sequentially** based on the user query.

### Sub‑agents (tools)

All sub‑agents are defined in `my_agent/agent.py`:

- `QueryAgent` (`output_key="trip_params"`): parses the user question into structured trip parameters.
- `InformationAgent` (`output_key="trip_info"`): suggests flights, hotels, and activities with rich, actionable sections.
- `BudgetAgent` (`output_key="cost_estimate"`): builds a budget breakdown in INR/EUR with Low / Medium / High scenarios and tips.
- `ItineraryAgent` (`output_key="itinerary"`): creates a day‑wise plan with blocks, transit, time, and estimated costs.
- `ValidatorAgent` (`output_key="validation_status"`): checks the itinerary for feasibility and either returns `valid` or suggests corrections.
- `PresenterAgent` (`output_key="final_plan_draft"`): composes a comprehensive draft answer from upstream state.
- `PolisherAgent` (`output_key="final_plan"`): enforces a quality rubric and emits the single final response.

### Shared session state

Agents cooperate via `ctx.session.state`. Key entries include:

- `trip_params`, `trip_info`, `cost_estimate`, `itinerary`, `validation_status`, `final_plan_draft`, `final_plan`.
- Keys are default‑initialized to empty strings in the loop to prevent template key errors when formatting prompts.

---

## Routing (non‑sequential)

Routing is implemented in `CheckLoopAgent._run_async_impl()` in `my_agent/agent.py`:

- Always run `QueryAgent` first to populate `trip_params`.
- Inspect the (lowercased) user request for keywords and determine `route` with precedence:
  - `itinerary` **and** `budget` → `full` (run all main sub‑agents).
  - `itinerary` → `itinerary`.
  - `budget` → `budget`.
  - `info` or related terms → `info`.
  - Otherwise → default `full`.
- Execute only the agents required for the chosen route, silently consuming their events.
- Generate a draft via `PresenterAgent`, then polish and emit the final answer via `PolisherAgent`.

### Single final response

- Intermediate sub‑agent events are not exposed to the UI; only `PolisherAgent` output is returned.
- After emitting the final message, the loop yields an escalate event so ADK can terminate the interaction cleanly.

---

## Models

- All LLM agents currently use `gemini-2.5-flash`.
- You can change models by editing the `model=` values in `my_agent/agent.py` (for example, to use different Gemini variants per agent, or to satisfy quota constraints).

---

## Testing

- A ready‑made test set lives in `my_agent/test.md` (about 25 questions).
- Each case documents:
  - The input question.
  - The expected routing (`info`, `budget`, `itinerary`, or `full`).
  - Which agents should run and why (based on router rules).

Use these prompts manually in the web UI to verify routing and outputs after changes.

---

## Example prompts

- “What’s the estimated budget for a 5‑day trip from Bengaluru to Paris starting 20 Nov 2025?” → `budget` route.
- “Create a 5‑day day‑wise itinerary for Paris and validate feasibility.” → `itinerary` route (plus validator).
- “Give me information about top activities in Paris for 5 days.” → `info` route.

---

## Troubleshooting

- **App name mismatch warning**  
  Non‑fatal; prefer starting the UI with `adk web . --port 8000` from the repository root.

- **Missing key errors**  
  Keys like `trip_info` and `itinerary` are default‑initialized in `_run_async_impl()`. If you add new state keys in prompts, also initialize them there.

- **Rate limits (HTTP 429)**  
  The router runs only the minimal set of agents per query. If you still hit rate limits, consider:
  - Spreading different models across agents.
  - Adding short delays between interactive runs.
  - Reducing verbosity or number of options returned by each agent.

---

## Repository structure (relevant)

- `my_agent/agent.py` – sub‑agents, router, planning loop, and root agent wiring.
- `my_agent/__init__.py` – exports `root_agent` for ADK discovery.
- `my_agent/architecture.md` – architecture diagram and rationale.
- `my_agent/test.md` – manual test questions and expected routing.

