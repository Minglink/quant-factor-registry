# 20 Day Average Dollar Volume (`average_dollar_volume_20`)

## Definition

The 20-day mean traded value. It uses `turnover` when provided, otherwise `close * volume`.

## Data and availability

Requires daily `close` and `volume`; the adapter must document volume units and whether turnover includes block trades. Values are usable only after the close.

## Evaluation and robustness

Use primarily as a liquidity screen or exposure. Report its relation to market capitalization and verify that high values do not arise from one-off events.

## Source and status

Replicated standard market-data measure. Definition reference: https://www.investor.gov/introduction-investing/investing-basics/glossary/volume. Version `0.1.0`.
