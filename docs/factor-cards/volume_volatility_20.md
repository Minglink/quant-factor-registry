# 20 Day Volume Volatility (`volume_volatility_20`)

## Definition

The rolling standard deviation of log daily volume. It measures unstable trading activity rather than price risk.

## Data and availability

Requires strictly positive daily `volume`, with documented source units. Values are known after the session and are available from the next session.

## Evaluation and robustness

This is experimental. Check for corporate actions, index rebalances and event days; report its correlation with dollar volume and turnover before adding it to a model.

## Source and status

Standard data-derived measure, with market-microstructure context in https://doi.org/10.1111/j.1540-6261.1990.tb05063.x. Version `0.1.0`.
