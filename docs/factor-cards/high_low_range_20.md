# 20 Day High-Low Range (`high_low_range_20`)

## Definition

The 20-day mean of `(high - low) / close`, a range-based proxy for realised trading variability.

## Data and availability

Requires daily `high`, `low` and adjusted `close`. These are end-of-session values, so trading begins no earlier than the next session.

## Evaluation and robustness

Compare with close-to-close volatility, report regime breakdowns and inspect data-quality sensitivity around price limits and corporate actions.

## Source and status

Replicated range measure; see Parkinson (1980), https://doi.org/10.1093/rfs/3.3.477. Version `0.1.0`.
