# Architecture: my_agent

```mermaid
flowchart TD
    U[User Question] --> RP[Root SequentialAgent: RootPlanner]
    RP --> MA[MasterAgent]
    MA --> PL[CheckLoopAgent: PlanningLoop]

    %% Always extract parameters first
    PL --> QP[QueryAgent\noutput_key: trip_params]

    %% Routing paths (non-sequential)
    QP -->|route=info| IA[InformationAgent\noutput_key: trip_info]
    QP -->|route=budget| IA2[InformationAgent] --> BA[BudgetAgent\noutput_key: cost_estimate]
    QP -->|route=itinerary| IA3[InformationAgent] --> IT[ItineraryAgent\noutput_key: itinerary]
    IT -->|if validate?| VA[ValidatorAgent\noutput_key: validation_status]
    QP -->|route=full| IA4[InformationAgent] --> BA2[BudgetAgent] --> IT2[ItineraryAgent] --> VA2[ValidatorAgent]

    %% Session state writes
    QP --> SP[(trip_params)]
    IA --> S1[(trip_info)]
    BA --> S2[(cost_estimate)]
    IT --> S3[(itinerary)]
    VA --> S4[(validation_status)]
    IA4 --> S1a[(trip_info)]
    BA2 --> S2a[(cost_estimate)]
    IT2 --> S3a[(itinerary)]
    VA2 --> S4a[(validation_status)]

    %% Finalization (single visible output)
    PL --> PR[PresenterAgent\noutput_key: final_plan_draft]
    PR --> POL[PolisherAgent\noutput_key: final_plan]
    POL --> FP[(session.state.final_plan)]
    POL --> OUT[Single Final Response]
```

## Why this is agentic (not just a bunch of agents)

- **[orchestration]** Top-level control (`root` → `master_agent` → `planning_loop`) plans and invokes sub-capabilities; agents don’t act independently.
- **[routing and policy]** `CheckLoopAgent._run_async_impl()` routes based on intent keywords with precedence. It chooses minimal necessary tools (agents) for the task instead of a fixed chain.
- **[stateful memory]** Agents cooperate through `ctx.session.state` keys like `trip_params`, `trip_info`, `cost_estimate`, `itinerary`, `validation_status`, `final_plan_draft`, `final_plan`.
- **[tool-like agents]** Sub-agents are treated as tools the planner calls in context, enabling reuse and modularity.
- **[quality gate]** A dedicated polishing stage enforces structure and completeness before emitting the final message.
- **[termination control]** The loop escalates after the polisher output, guaranteeing a single visible response per invocation.

## Routing rules (high level)

- **[always first]** `QueryAgent` extracts `trip_params` from the user question.
- **[info]** Keywords: info, information, flights, hotels, activities, options, agents → `InformationAgent`.
- **[budget]** Keywords: budget, cost, price, estimate → `InformationAgent` → `BudgetAgent`.
- **[itinerary]** Keywords: itinerary, day, schedule, day-wise, plan itinerary → `InformationAgent` → `ItineraryAgent`; add `ValidatorAgent` if validate/feasible/valid present.
- **[full]** If both itinerary and budget are requested or nothing matches → run all four sub-agents.