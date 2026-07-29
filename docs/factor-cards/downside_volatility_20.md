# 20 Day Downside Volatility (`downside_volatility_20`)

## Definition

The rolling standard deviation of daily returns after positive returns are replaced with zero. It focuses the risk measure on adverse price movement.

## Data and availability

Requires adjusted daily `close`; all information is available after the close and can first be acted on at the next session.

## Evaluation and robustness

Evaluate both raw and industry/size-neutralized values. Compare across bull, bear and high-volatility regimes; do not interpret a low-volatility premium without capacity and cost checks.

## Source and status

Replicated daily-risk measure; see Schwert (1989), https://doi.org/10.2307/2329167. Version `0.1.0`.
