# 20 Day Return Skewness (`return_skewness_20`)

## Definition

The rolling sample skewness of daily simple returns over 20 sessions. It describes asymmetry in the recent return distribution.

## Data and availability

Requires adjusted daily `close`. The signal uses only completed sessions and is actionable from the next session.

## Evaluation and robustness

This is experimental. Use sufficient observations, winsorize only in a documented preprocessing step and inspect stability across volatility regimes and size buckets.

## Source and status

Standard distributional measure; asset-pricing context: https://doi.org/10.1016/j.jfineco.2005.05.003. Version `0.1.0`.
