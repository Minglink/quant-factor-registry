# 60 Day Momentum (`momentum_60`)

## Definition

`close[t] / close[t-60] - 1`. It captures a medium-term price trend.

## Data and availability

Requires adjusted `close` in canonical daily bars. Use the value after the close only in the next trading session and record all universe filters.

## Evaluation and robustness

Report standard cross-sectional diagnostics over full history, size buckets and market regimes. Measure correlation with shorter and 12-1 momentum before use in a composite.

## Source and status

Replicated from Jegadeesh and Titman (1993): https://doi.org/10.1111/j.1540-6261.1993.tb04702.x. Version `0.1.0`.
