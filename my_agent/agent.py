from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.events import Event, EventActions

# Define sub-agents

info_agent = LlmAgent(
    name="InformationAgent",
    instruction=(
        "You are an expert trip researcher. "
        "Given the destination and dates, find flight options, hotel options, and top activities."
    ),
    output_key="trip_info",
    model="gemini-2.5-flash"
)

budget_agent = LlmAgent(
    name="BudgetAgent",
    instruction=(
        "You are a budget analyst. Use the data in {trip_info} to estimate the total cost "
        "for flights, accommodation, and activities. If it's over the user's budget, suggest cheaper options."
    ),
    output_key="cost_estimate",
    model="gemini-2.5-flash"
)

itinerary_agent = LlmAgent(
    name="ItineraryAgent",
    instruction=(
        "You are a travel planner. Build a day-wise itinerary for the trip based on {trip_info}. "
        "Optimize for travel convenience and experiences."
    ),
    output_key="itinerary",
    model="gemini-2.5-flash"
)

validator_agent = LlmAgent(
    name="ValidatorAgent",
    instruction=(
        "You are a validator. Check if the itinerary in {itinerary} is feasible: "
        "check travel times, realistic day plans, and any logical inconsistencies. "
        "If valid, respond with 'valid'. If not, describe the issues."
    ),
    output_key="validation_status",
    model="gemini-2.5-flash"
)

presenter_agent = LlmAgent(
    name="PresenterAgent",
    instruction=(
        "You are the final presenter. Use any available of {trip_info}, {cost_estimate}, {itinerary}, and {validation_status} "
        "to produce a single concise answer tailored to the user's question. If {validation_status} indicates issues, explain them "
        "and provide a corrected or alternative high-level plan."
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

            route = "full"
            if any(w in q for w in ["budget", "cost", "price", "estimate"]):
                route = "budget"
            if any(w in q for w in ["itinerary", "day", "schedule", "day-wise", "plan itinerary"]):
                route = "itinerary" if route != "budget" else "full"
            if any(w in q for w in ["info", "information", "flights", "hotels", "activities", "options", "agents"]):
                route = "info" if route != "full" else "full"
            validate = any(w in q for w in ["validate", "feasible", "check validity", "valid"])

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

            async for event in presenter_agent.run_async(ctx):
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
