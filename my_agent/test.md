# Test Questions for my_agent Routing

Note: According to current routing in `CheckLoopAgent._run_async_impl()` in `my_agent/agent.py`:
- Default `route` is `full` and remains `full` for pure info queries due to logic precedence.
- `info` keywords can override `budget` or `itinerary` to `info` if present together.
- `validate` only adds `ValidatorAgent` automatically when `route` is `itinerary`; otherwise `full` already includes it.
- `PresenterAgent` always runs last to emit a single final response.

| ID | Test question | Expected route | Agents invoked | Reason |
|---:|---|---|---|---|
| 1 | What flight and hotel options are available from Bengaluru to Paris on 20 Nov 2025? | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Pure info keywords but default starts at `full`; info condition keeps `full` when already `full`. |
| 2 | Give me information about top activities in Paris for 5 days. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Info-only query; default `full` persists. |
| 3 | What all agents do you have and what can they do? | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Contains "agents" (info keyword) but default `full` remains. |
| 4 | What’s the estimated budget for a 5-day trip from Bengaluru to Paris starting 20 Nov 2025? | budget | InformationAgent, BudgetAgent, PresenterAgent | Contains budget keywords → `budget` route. |
| 5 | Cost estimate for flights, accommodation, and activities for 5 days in Paris. | budget | InformationAgent, BudgetAgent, PresenterAgent | Budget keywords → `budget`. |
| 6 | Price breakdown for a 5-day Paris trip including flights and hotel. | budget | InformationAgent, BudgetAgent, PresenterAgent | Budget synonyms → `budget`. |
| 7 | Create a 5-day day-wise itinerary for Paris starting 20 Nov 2025. | itinerary | InformationAgent, ItineraryAgent, PresenterAgent | Itinerary keywords → `itinerary`. |
| 8 | Plan itinerary for Paris for 5 days. | itinerary | InformationAgent, ItineraryAgent, PresenterAgent | Matches "plan itinerary" keyword. |
| 9 | Give me a schedule for 5 days in Paris with must-see attractions. | itinerary | InformationAgent, ItineraryAgent, PresenterAgent | "schedule", "day" keywords → `itinerary`. |
| 10 | Plan a 5-day itinerary for Paris and validate if it’s feasible. | itinerary (+validate) | InformationAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Itinerary + validate keywords → run validator after itinerary. |
| 11 | Is this 5-day Paris itinerary feasible? If not, fix it. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Contains "valid/feasible" but no itinerary keywords; default remains `full` which includes validator. |
| 12 | Validate the feasibility of a 5-day Paris plan. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Validate only → `full`. |
| 13 | I need a full plan: info, budget, and itinerary for 5 days in Paris from 20 Nov 2025. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Explicitly full. |
| 14 | Prepare an itinerary and estimate budget for a 5-day Paris trip. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Contains both itinerary and budget → code sets `full`. |
| 15 | Give me flight options and a budget estimate for Paris. | info overrides budget (current logic) | InformationAgent, PresenterAgent | Info keywords appear after budget logic; info condition overrides to `info` when route != full. |
| 16 | Provide hotel options and a day-wise itinerary. | info overrides itinerary (current logic) | InformationAgent, PresenterAgent | Info keywords present; after itinerary sets route, info condition switches it to `info`. |
| 17 | What’s the budget estimate? Validate the plan too. | budget | InformationAgent, BudgetAgent, PresenterAgent | Budget + validate but no itinerary keywords → stays `budget`; validator not invoked in `budget` route. |
| 18 | Build an itinerary, check feasibility, and estimate total cost. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Itinerary + validate + cost → `full`. |
| 19 | Help me plan a 5-day Paris trip. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | No strong keywords → default `full`. |
| 20 | List activities and top neighborhoods in Paris. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Info-only → remains `full`. |
| 21 | Cheapest flight options for 20 Nov from BLR to CDG. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Info + price word "cheapest" doesn’t map to budget keyword list; defaults to `full`. |
| 22 | Show just the day schedule for a weekend in Paris. | itinerary | InformationAgent, ItineraryAgent, PresenterAgent | Itinerary keywords → `itinerary`. |
| 23 | Provide options and a rough price estimate for 3 days in Paris. | budget (if "price" considered budget) | InformationAgent, BudgetAgent, PresenterAgent | Contains "price" → `budget`. |
| 24 | Validate this itinerary for travel times between attractions. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Validate only → `full`. |
| 25 | I want info on flights and hotels only, no itinerary or budget. | full | InformationAgent, BudgetAgent, ItineraryAgent, ValidatorAgent, PresenterAgent | Info-only still routes to `full` under current logic.

Footnote: If you prefer info-only queries to run just `InformationAgent`, adjust routing so that when only info keywords are present, `route` is set to `info` instead of sticking with `full`.
