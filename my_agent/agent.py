from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.events import Event, EventActions

# Define sub-agents

query_agent = LlmAgent(
    name="QueryAgent",
    instruction=(
        "Parse the user's question into structured trip parameters. Output concise JSON only with keys: "
        "origin, destination, departure_date, return_date, trip_length_days, headcount, budget_value, budget_currency, preferences. "
        "If a field is unknown, set it to null."
    ),
    output_key="trip_params",
    model="gemini-2.5-flash"
)

info_agent = LlmAgent(
    name="InformationAgent",
    instruction=(
        "You are an expert trip researcher. Use {trip_params} (if available) and the user's question to ground details.\n"
        "Respond with rich, actionable content in Markdown using these sections:\n"
        "### Flights (3-5 options)\n"
        "- Airline | Route | Duration | Layovers | Typical price range | Booking tips\n"
        "### Hotels (3-5 options across budget tiers)\n"
        "- Name | Neighborhood | Tier | Nightly price | Total for stay | Pros/Cons\n"
        "### Activities (6-10)\n"
        "- Name | Est. cost | Time needed | Booking window | Notes\n"
        "### Assumptions\n"
        "- Explicitly state defaults if dates or counts are missing. Aim for 250-500 words."
    ),
    output_key="trip_info",
    model="gemini-2.5-flash"
)

budget_agent = LlmAgent(
    name="BudgetAgent",
    instruction=(
        "You are a budget analyst. Using {trip_params} and {trip_info}, build a clear budget breakdown in INR and EUR.\n"
        "Include line items: Flights, Accommodation (nightly x nights), Activities, Local Transport, Food, Misc (SIM, tips).\n"
        "Provide totals for Low / Medium / High scenarios as a Markdown table.\n"
        "State assumptions (FX rate; if unspecified assume 1 EUR ≈ 100 INR), and list 3-5 saving tips if over budget. Aim for 150-300 words."
    ),
    output_key="cost_estimate",
    model="gemini-2.5-flash"
)

itinerary_agent = LlmAgent(
    name="ItineraryAgent",
    instruction=(
        "You are a travel planner. Build a realistic day-wise itinerary (Day 1..N) using {trip_info} and {trip_params}.\n"
        "For each day list Morning / Afternoon / Evening blocks with: Place | Est. time | Transit (mode & duration) | Est. cost.\n"
        "Cluster sights by area to reduce transit; add backup options and note booking-required items. Aim for 250-500 words."
    ),
    output_key="itinerary",
    model="gemini-2.5-flash"
)

validator_agent = LlmAgent(
    name="ValidatorAgent",
    instruction=(
        "You are a validator. Check {itinerary} for feasibility: transit times, opening hours, overbooking, and logical flow.\n"
        "If feasible, respond only with 'valid'. If not feasible, list specific issues and provide concise corrections."
    ),
    output_key="validation_status",
    model="gemini-2.5-flash"
)

presenter_agent = LlmAgent(
    name="PresenterAgent",
    instruction=(
        "Draft a comprehensive answer using {trip_info}, {cost_estimate}, {itinerary}, and {validation_status}.\n"
        "Include sections: Overview, Extracted Parameters, Flights, Hotels, Day-by-day Itinerary, Budget Breakdown (tables), Tips, Assumptions.\n"
        "Reflect corrections if {validation_status} is not 'valid'. Aim for 500-800 words."
    ),
    output_key="final_plan_draft",
    model="gemini-2.5-flash"
)

polisher_agent = LlmAgent(
    name="PolisherAgent",
    instruction=(
        "You are a rigorous editor. Improve the following draft {final_plan_draft} into a single, well-structured final answer.\n"
        "Apply this rubric:\n"
        "- Ensure all sections are present and populated (Overview, Parameters, Flights, Hotels, Itinerary, Budget table, Tips, Assumptions).\n"
        "- Add missing specifics using {trip_params} and {trip_info} if available; avoid contradictions.\n"
        "- Make the budget a Markdown table with totals and currency notes; compare to any stated budget.\n"
        "- Remove meta text and ensure the tone is helpful and concise. Output only the final answer."
    ),
    output_key="final_plan",
    model="gemini-2.5-flash"
)

# Optionally a loop agent to retry if validation fails
def make_loop_agent(max_iters=1):
    class CheckLoopAgent(LoopAgent):
        def __init__(self, sub_agents):
            super().__init__(name="PlanningLoop", sub_agents=sub_agents, max_iterations=max_iters)

        async def _run_async_impl(self, ctx):
            q = ""
            for k in ["user_request", "user_input", "query", "prompt", "message", "input", "text"]:
                v = ctx.session.state.get(k, "")
                if isinstance(v, str) and v:
                    q = v.lower()
                    break

            # ensure placeholders used in downstream instructions always exist
            for key in ("trip_params", "trip_info", "cost_estimate", "itinerary", "validation_status", "final_plan_draft"):
                if key not in ctx.session.state:
                    ctx.session.state[key] = ""

            # propagate discovered query to a canonical key for downstream prompts
            if not ctx.session.state.get("user_request"):
                raw = ctx.session.state.get("input") or ctx.session.state.get("text") or ctx.session.state.get("message") or ""
                if isinstance(raw, str):
                    ctx.session.state["user_request"] = raw

            # always extract structured parameters first
            async for _ in query_agent.run_async(ctx):
                pass

            # Decide route based on keywords with clearer precedence
            info_kw = any(w in q for w in ["info", "information", "flights", "hotels", "activities", "options", "agents"])
            budget_kw = any(w in q for w in ["budget", "cost", "price", "estimate"])
            itin_kw = any(w in q for w in ["itinerary", "day", "schedule", "day-wise", "plan itinerary"])
            validate = any(w in q for w in ["validate", "feasible", "check validity", "valid"])

            route = None
            if itin_kw and budget_kw:
                route = "full"
            elif itin_kw:
                route = "itinerary"
            elif budget_kw:
                route = "budget"
            elif info_kw:
                route = "info"
            else:
                route = "full"

            if route == "info":
                async for _ in info_agent.run_async(ctx):
                    pass
            elif route == "budget":
                async for _ in info_agent.run_async(ctx):
                    pass
                async for _ in budget_agent.run_async(ctx):
                    pass
            elif route == "itinerary":
                async for _ in info_agent.run_async(ctx):
                    pass
                async for _ in itinerary_agent.run_async(ctx):
                    pass
                if validate:
                    async for _ in validator_agent.run_async(ctx):
                        pass
            else:
                for agent in [info_agent, budget_agent, itinerary_agent, validator_agent]:
                    async for _ in agent.run_async(ctx):
                        pass

            # produce draft silently, then yield only polished final
            async for _ in presenter_agent.run_async(ctx):
                pass

            async for event in polisher_agent.run_async(ctx):
                yield event

            yield Event(author=self.name, actions=EventActions(escalate=True))
            return

    # The loop includes info → budget → itinerary → validator
    return CheckLoopAgent(sub_agents=[info_agent, budget_agent, itinerary_agent, validator_agent])

planning_loop = make_loop_agent(max_iters=1)

# Master agent that orchestrates
master_agent = SequentialAgent(
    name="MasterAgent",
    sub_agents=[planning_loop]
)

# Now build a workflow: sequentially call master
root = SequentialAgent(
    name="RootPlanner",
    sub_agents=[master_agent]
)

root_agent = root

# Running the system (pseudo)
def run_trip_planner(user_input):
    # user_input could be something like {"destination":"Paris", "dates":"2025-12-01 to 2025-12-06", "budget": 250000}
    # Store in session state
    # (Assume ADK has a session or context builder; pseudo-code)
    session = root.run({"user_request": user_input})
    return session.state.get("final_plan")

# Example usage:
if __name__ == "__main__":
    plan = run_trip_planner({
        "destination": "Paris",
        "dates": "2025-12-01 to 2025-12-06",
        "budget": 250000
    })
    print("Final Trip Plan:\n", plan)
