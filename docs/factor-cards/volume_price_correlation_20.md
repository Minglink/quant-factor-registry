# 20 Day Volume-Price Correlation (`volume_price_correlation_20`)

## Definition

The rolling correlation between daily simple returns and log-volume changes. It captures whether price moves occur with expanding or contracting activity.

## Data and availability

Requires adjusted `close` and strictly positive `volume`. A zero-variance window has no defined correlation and is intentionally omitted from output. Signals are usable from the next session.

## Evaluation and robustness

This is experimental. Test separately by liquidity bucket, market state and exchange; report missing-value coverage and transaction-cost-adjusted returns.

## Source and status

Standard data-derived measure; volume-price research context: https://doi.org/10.1016/j.jfineco.2009.09.004. Version `0.1.0`.
