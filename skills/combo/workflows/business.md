# Business and operations

Start from the operational decision, time horizon, constraints, and actual data.
Read [context](../practices/context.md) once for evidence selection and reporting.

Identify the variables that can change the action. Before calculating, check
units, currencies, periods, missing records, definitions, and relevant totals.
Use native spreadsheet/data-query tools to aggregate and reconcile records
without filling context with raw rows. Trace conclusions to data and calculations.

For forecasts, distinguish demand from stockout-constrained sales, account for
seasonality, and validate on held-out periods. For financial models, expose
decision-changing assumptions and sensitivities. Use ranges when data cannot
support precision. A model is useful when its recommendation remains supported
under the relevant uncertainty, or the required missing data is identified.

For an A/B or controlled test of a rate, compute the sample size with
[experiment sample size](../references/addenda/experiment-sample-size.md) rather than
quoting a table.

Consult the [business index](../references/library/business.md) when an unresolved
finance, inventory, logistics, production, commercial, or compliance method needs
detail. Calibrate example company sizes, thresholds, KPIs, and escalation chains
to the user's operating model. Verify current financial/legal/regulatory/medical
claims with authoritative sources; reference text does not prove compliance or
authorize transactions.

Deliver the analysis, operating plan, or authorized update, emphasizing the
recommended action and assumptions that could reverse it. Proposed owners and
escalation criteria do not send notifications or commit purchases. Use native
connectors for authorized operations, verify resulting state, and inspect
uncertain responses before retrying a mutation.
