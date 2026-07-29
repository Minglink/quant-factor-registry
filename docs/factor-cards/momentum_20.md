# 20 Day Momentum (`momentum_20`)

## Definition

`close[t] / close[t-20] - 1`. It measures a one-month trailing price trend.

## Data and availability

Requires adjusted `close` in canonical daily bars. The close is only tradable from the next session; suspended, limit-up/down, new-listing and ST filters belong in the experiment universe.

## Evaluation and robustness

Report Rank IC, quantile spread, turnover and cost-adjusted spread over full history and by market regime. Compare with `momentum_60` and `momentum_12_1` before combining.

## Source and status

Replicated from Jegadeesh and Titman (1993): https://doi.org/10.1111/j.1540-6261.1993.tb04702.x. Version `0.1.0`.
