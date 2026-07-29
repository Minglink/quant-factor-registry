# 20 Day Reversal (`reversal_20`)

## Definition

The negative of the trailing 20-day return. Higher values denote recent relative underperformance.

## Data and availability

Requires adjusted daily `close`. The close is only available after the session; the universe must explicitly handle suspensions and price limits.

## Evaluation and robustness

Report IC, gross and cost-adjusted quantile spread, turnover and regime breakdowns. Compare with `reversal_5` because both express the same broad economic mechanism.

## Source and status

Replicated from Jegadeesh (1990): https://doi.org/10.1111/j.1540-6261.1990.tb05063.x. Version `0.1.0`.
